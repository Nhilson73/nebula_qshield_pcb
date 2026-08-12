#!/usr/bin/env python3
import re, math, pcbnew

MM = 1_000_000
BOARD_PATH = '/workspace/kicad/nebula_qshield.kicad_pcb'
DRC_PATH = '/workspace/nebula_qshield-drc.rpt'

brd = pcbnew.LoadBoard(BOARD_PATH)

def get_pad_rect(p):
    bb = p.GetBoundingBox()
    return (bb.GetX() / MM, bb.GetY() / MM, (bb.GetX() + bb.GetWidth()) / MM, (bb.GetY() + bb.GetHeight()) / MM)

def rect_dist(px, py, r):
    x1, y1, x2, y2 = r
    dx = max(max(x1 - px, 0.0), px - x2)
    dy = max(max(y1 - py, 0.0), py - y2)
    return math.hypot(dx, dy)

def seg_dist(px, py, x1, y1, x2, y2):
    dx = x2 - x1; dy = y2 - y1
    seg = math.hypot(dx, dy)
    if seg == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / seg / seg
    t = max(0.0, min(1.0, t))
    cx = x1 + t * dx; cy = y1 + t * dy
    return math.hypot(px - cx, py - cy)

def build_bcu_obstacles(via_r=0.25, clearance=0.25):
    obs = []
    safe = via_r + clearance
    for t in brd.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            if not t.GetLayerSet().Contains(pcbnew.B_Cu):
                continue
            if t.GetNetname() == 'GND':
                continue
            pos = t.GetPosition()
            r = t.GetWidth(pcbnew.B_Cu) / 2.0 / MM
            obs.append(('via', pos.x / MM, pos.y / MM, r, safe))
        elif isinstance(t, pcbnew.PCB_TRACK):
            if t.GetLayer() != pcbnew.B_Cu:
                continue
            if t.GetNetname() == 'GND':
                continue
            r = t.GetWidth() / 2.0 / MM
            s = t.GetStart(); e = t.GetEnd()
            obs.append(('track', s.x / MM, s.y / MM, e.x / MM, e.y / MM, r, safe))
    for fp in brd.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == 'GND':
                continue
            if not p.GetLayerSet().Contains(pcbnew.B_Cu):
                continue
            obs.append(('pad',) + get_pad_rect(p) + (safe,))
    return obs

def bcu_safe(x, y, obs, via_r=0.25, clearance=0.25):
    safe = via_r + clearance
    for ob in obs:
        if ob[0] == 'via':
            _, vx, vy, r, _safe = ob
            d = math.hypot(x - vx, y - vy)
            margin = d - r - safe
        elif ob[0] == 'track':
            _, x1, y1, x2, y2, r, _safe = ob
            d = seg_dist(x, y, x1, y1, x2, y2)
            margin = d - r - safe
        else:
            _, x1, y1, x2, y2, _safe = ob
            d = rect_dist(x, y, (x1, y1, x2, y2))
            margin = d - safe
        if margin < 0:
            return False
    return True

text = open(DRC_PATH).read()
coords = set()
for m in re.finditer(r'@\(([-\d\.]+) mm, ([-\d\.]+) mm\): (?:Pad \d+|Track|Via) \[GND\]', text):
    coords.add((float(m.group(1)), float(m.group(2))))

pad_by_center = {}
for fp in brd.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname() == 'GND' and p.GetAttribute() == 1:
            rect = get_pad_rect(p)
            cx = (rect[0]+rect[2])/2.0
            cy = (rect[1]+rect[3])/2.0
            pad_by_center[(round(cx,4), round(cy,4))] = (fp, p, rect)

gnd_net = brd.FindNet('GND')
bcu_obs = build_bcu_obstacles()

via_d = 0.5
via_r = via_d / 2.0
drill = 0.2

placed = 0
skipped = 0
for (x, y) in coords:
    key = (round(x,4), round(y,4))
    if key not in pad_by_center:
        skipped += 1
        continue
    fp, p, rect = pad_by_center[key]
    cx = (rect[0]+rect[2])/2.0
    cy = (rect[1]+rect[3])/2.0
    candidates = []
    for dx in [0.0, 0.04, -0.04, 0.08, -0.08, 0.12, -0.12, 0.16, -0.16]:
        for dy in [0.0, 0.04, -0.04, 0.08, -0.08, 0.12, -0.12, 0.16, -0.16]:
            candidates.append((cx+dx, cy+dy))
    found = False
    for px, py in candidates:
        if px < rect[0] + via_r or px > rect[2] - via_r or py < rect[1] + via_r or py > rect[3] - via_r:
            continue
        if bcu_safe(px, py, bcu_obs, via_r, 0.25):
            via = pcbnew.PCB_VIA(brd)
            via.SetPosition(pcbnew.VECTOR2I(int(round(px*MM)), int(round(py*MM))))
            via.SetNet(gnd_net)
            via.SetWidth(int(round(via_d*MM)))
            via.SetDrill(int(round(drill*MM)))
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            via.SetRemoveUnconnected(False)
            brd.Add(via)
            placed += 1
            bcu_obs.append(('via', px, py, via_r, via_r+0.25))
            found = True
            break
    if not found:
        skipped += 1

print('placed', placed, 'skipped', skipped)
for z in brd.Zones():
    if z.GetNetname() == 'GND':
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetThermalReliefGap(200000)
        z.SetThermalReliefSpokeWidth(200000)

filler = pcbnew.ZONE_FILLER(brd)
filler.Fill(brd.Zones())
brd.BuildConnectivity()
pcbnew.SaveBoard(BOARD_PATH, brd)
print('Saved')
