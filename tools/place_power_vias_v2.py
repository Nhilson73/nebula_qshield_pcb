#!/usr/bin/env python3
"""Place 0.5/0.2 vias on unconnected power pads/tracks to connect them to the In2.Cu split-plane."""
import re, math, pcbnew

MM = 1_000_000
BOARD_PATH = '/workspace/kicad/nebula_qshield.kicad_pcb'
DRC_PATH = '/workspace/nebula_qshield-drc.rpt'
VIA_D = 0.5
DRILL = 0.2
VR = VIA_D / 2.0

brd = pcbnew.LoadBoard(BOARD_PATH)

def get_pad_rect(p):
    bb = p.GetBoundingBox()
    return (bb.GetX()/MM, bb.GetY()/MM, (bb.GetX()+bb.GetWidth())/MM, (bb.GetY()+bb.GetHeight())/MM)

def rect_dist(px, py, r):
    x1,y1,x2,y2 = r
    dx = max(max(x1-px, 0.0), px-x2)
    dy = max(max(y1-py, 0.0), py-y2)
    return math.hypot(dx, dy)

def seg_dist(px, py, x1, y1, x2, y2):
    dx=x2-x1; dy=y2-y1
    l2=dx*dx+dy*dy
    if l2==0: return math.hypot(px-x1, py-y1)
    t=max(0.0,min(1.0,((px-x1)*dx+(py-y1)*dy)/l2))
    cx=x1+t*dx; cy=y1+t*dy
    return math.hypot(px-cx, py-cy)

def orient(ax, ay, bx, by, cx, cy): return (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
def on_seg(ax, ay, bx, by, cx, cy): return min(ax,bx)<=cx<=max(ax,bx) and min(ay,by)<=cy<=max(ay,by)

def segments_intersect(x1,y1,x2,y2,x3,y3,x4,y4):
    o1=orient(x1,y1,x2,y2,x3,y3); o2=orient(x1,y1,x2,y2,x4,y4)
    o3=orient(x3,y3,x4,y4,x1,y1); o4=orient(x3,y3,x4,y4,x2,y2)
    if o1==0 and on_seg(x1,y1,x2,y2,x3,y3): return True
    if o2==0 and on_seg(x1,y1,x2,y2,x4,y4): return True
    if o3==0 and on_seg(x3,y3,x4,y4,x1,y1): return True
    if o4==0 and on_seg(x3,y3,x4,y4,x2,y2): return True
    return (o1>0)!=(o2>0) and (o3>0)!=(o4>0)

def seg_to_seg_dist(x1,y1,x2,y2,x3,y3,x4,y4):
    if segments_intersect(x1,y1,x2,y2,x3,y3,x4,y4): return 0.0
    def sdp(px,py,ax,ay,bx,by):
        dx=bx-ax; dy=by-ay; l2=dx*dx+dy*dy
        if l2==0: return math.hypot(px-ax,py-ay)
        t=max(0.0,min(1.0,((px-ax)*dx+(py-ay)*dy)/l2))
        return math.hypot(px-(ax+t*dx), py-(ay+t*dy))
    return min(sdp(x1,y1,x3,y3,x4,y4), sdp(x2,y2,x3,y3,x4,y4), sdp(x3,y3,x1,y1,x2,y2), sdp(x4,y4,x1,y1,x2,y2))

def rect_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2):
    dmin=float('inf')
    for a,b,c,d in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]:
        dmin=min(dmin, seg_to_seg_dist(a,b,c,d,sx1,sy1,sx2,sy2))
    return dmin

def netclass_clearance(netname, other_net):
    if 'Analog' in netname or 'Analog' in other_net or '_SIG' in netname or '_ADC' in netname or '_FILT' in netname or '_ATT' in netname:
        return 0.35
    if any(s in netname or s in other_net for s in ['/12V','/5V','/3V3','VIN_12V','12V_FUSED','CHILLER','MOTOR','COIL','/Actuator']):
        return 0.30
    if 'I2C' in netname or 'I2C' in other_net:
        return 0.25
    return 0.25

class ObstacleSet:
    def __init__(self, brd, layer_id):
        self.vias=[]; self.tracks=[]; self.pads=[]; self.layer=layer_id
        for t in brd.GetTracks():
            if isinstance(t, pcbnew.PCB_VIA):
                if not t.GetLayerSet().Contains(layer_id): continue
                r = t.GetWidth(layer_id)/2.0/MM
                pos=t.GetPosition()
                self.vias.append((pos.x/MM, pos.y/MM, r, t.GetNetname()))
            elif isinstance(t, pcbnew.PCB_TRACK):
                if t.GetLayer()!=layer_id: continue
                r=t.GetWidth()/2.0/MM
                s=t.GetStart(); e=t.GetEnd()
                self.tracks.append((s.x/MM,s.y/MM,e.x/MM,e.y/MM,r,t.GetNetname()))
        for fp in brd.GetFootprints():
            for p in fp.Pads():
                if not p.GetLayerSet().Contains(layer_id): continue
                rect=get_pad_rect(p)
                self.pads.append((rect[0],rect[1],rect[2],rect[3],p.GetNetname()))
    def point_safe(self, x, y, radius, net):
        for vx,vy,r,n in self.vias:
            if n==net: continue
            if math.hypot(x-vx,y-vy) - r - radius - netclass_clearance(net,n) < -0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            if seg_dist(x,y,sx1,sy1,sx2,sy2) - r - radius - netclass_clearance(net,n) < -0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            if rect_dist(x,y,(px1,py1,px2,py2)) - radius - netclass_clearance(net,n) < -0.001: return False
        return True
    def track_clear(self, x1,y1,x2,y2,width,net):
        hw=width/2.0
        for vx,vy,r,n in self.vias:
            if n==net: continue
            if seg_dist(vx,vy,x1,y1,x2,y2) - r - hw - netclass_clearance(net,n) < -0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            if seg_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2) - r - hw - netclass_clearance(net,n) < -0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            if rect_to_seg_dist(px1,py1,px2,py2,x1,y1,x2,y2) - hw - netclass_clearance(net,n) < -0.001: return False
        return True
    def add_via(self, x,y,r,net): self.vias.append((x,y,r,net))
    def add_track(self, x1,y1,x2,y2,w,net): self.tracks.append((x1,y1,x2,y2,w/2.0,net))

f_obs = ObstacleSet(brd, pcbnew.F_Cu)
b_obs = ObstacleSet(brd, pcbnew.B_Cu)

# Parse DRC
text = open(DRC_PATH).read()
blocks = re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    for line in block.split('\n'):
        m = re.match(r'\s+@\(([-\d\.]+) mm, ([-\d\.]+) mm\): (Pad \d+|Track|Via) \[([^\]]+)\](?: of ([^\n]+?))? on ([\w\. \-]+)', line)
        if m:
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer_raw':m.group(6).strip()})
    if len(items)==2:
        pairs.append(items)

power_nets = {'/12V_RAIL','/5V_RAIL','/3V3_RAIL'}
pairs = [p for p in pairs if p[0]['net'] in power_nets]
print('power pairs', len(pairs))

# index pads
pad_by_ref={}
for fp in brd.GetFootprints():
    for p in fp.Pads():
        pad_by_ref[(fp.GetReference(), str(p.GetNumber()))] = (fp, p, get_pad_rect(p))

def pad_of(it):
    if 'Pad ' in it['type']:
        return pad_by_ref.get((it['ref'], it['type'].split()[-1]))
    return None

def find_pad_pos(ref, num):
    fp=brd.FindFootprintByReference(ref)
    if fp:
        for p in fp.Pads():
            if str(p.GetNumber())==num:
                return p.GetPosition().x/MM, p.GetPosition().y/MM
    return None

existing_vias = set()
for t in brd.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        existing_vias.add((round(t.GetPosition().x/MM,3), round(t.GetPosition().y/MM,3), t.GetNetname()))

def add_via(x, y, net):
    k=(round(x,3), round(y,3), net.GetNetname())
    if k in existing_vias: return False
    if not f_obs.point_safe(x,y,VR,net.GetNetname()) or not b_obs.point_safe(x,y,VR,net.GetNetname()):
        return False
    via = pcbnew.PCB_VIA(brd)
    via.SetPosition(pcbnew.VECTOR2I(int(round(x*MM)), int(round(y*MM))))
    via.SetNet(net)
    via.SetWidth(int(round(VIA_D*MM)))
    via.SetDrill(int(round(DRILL*MM)))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetRemoveUnconnected(False)
    brd.Add(via)
    f_obs.add_via(x,y,VR,net.GetNetname())
    b_obs.add_via(x,y,VR,net.GetNetname())
    existing_vias.add(k)
    return True

def add_track(x1,y1,x2,y2, layer_id, width, net, obs):
    if obs.track_clear(x1,y1,x2,y2,width,net.GetNetname()):
        t = pcbnew.PCB_TRACK(brd)
        t.SetStart(pcbnew.VECTOR2I(int(round(x1*MM)), int(round(y1*MM))))
        t.SetEnd(pcbnew.VECTOR2I(int(round(x2*MM)), int(round(y2*MM))))
        t.SetLayer(layer_id)
        t.SetWidth(int(round(width*MM)))
        t.SetNet(net)
        brd.Add(t)
        obs.add_track(x1,y1,x2,y2,width,net.GetNetname())
        return True
    return False

def place_via_in_pad(it, net):
    info = pad_of(it)
    if not info: return None
    fp, p, rect = info
    cx=(rect[0]+rect[2])/2.0; cy=(rect[1]+rect[3])/2.0
    # search inside pad
    for dx in [0, 0.05, -0.05, 0.1, -0.1, 0.15, -0.15, 0.2, -0.2]:
        for dy in [0, 0.05, -0.05, 0.1, -0.1, 0.15, -0.15, 0.2, -0.2]:
            px, py = cx+dx, cy+dy
            if px < rect[0]+VR or px > rect[2]-VR or py < rect[1]+VR or py > rect[3]-VR:
                continue
            if f_obs.point_safe(px,py,VR,net.GetNetname()) and b_obs.point_safe(px,py,VR,net.GetNetname()):
                return (px,py)
    return None

def place_via_near_point(x, y, net):
    # try center and small spiral
    for r in [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]:
        for ang in [0, 0.785, 1.571, 2.356, 3.142, 3.927, 4.712, 5.498]:
            px = x + r*math.cos(ang)
            py = y + r*math.sin(ang)
            if f_obs.point_safe(px,py,VR,net.GetNetname()) and b_obs.point_safe(px,py,VR,net.GetNetname()):
                return (px,py)
    return None

def short_track_to_via(x, y, vx, vy, layer, width, net, obs):
    # straight track from (x,y) to via; if blocked, L-shape
    if obs.track_clear(x,y,vx,vy,width,net.GetNetname()):
        return add_track(x,y,vx,vy,layer,width,net,obs)
    # L-shape corners
    for mx in [x, vx, (x+vx)/2.0]:
        for my in [y, vy, (y+vy)/2.0]:
            if obs.track_clear(x,y,mx,my,width,net.GetNetname()) and obs.track_clear(mx,my,vx,vy,width,net.GetNetname()):
                return add_track(x,y,mx,my,layer,width,net,obs) and add_track(mx,my,vx,vy,layer,width,net,obs)
    return False

added_vias=0; added_tracks=0; skipped=0
for it1, it2 in pairs:
    net = brd.FindNet(it1['net'])
    if not net:
        skipped+=1; continue
    # Place via in/near each item
    pts = []
    for it in [it1, it2]:
        pos = None
        info = pad_of(it)
        if info:
            pos = place_via_in_pad(it, net)
            if pos:
                if add_via(pos[0], pos[1], net):
                    added_vias+=1
                    pts.append(pos)
                else:
                    pts.append(None)
                continue
        # track or no fit: try near item point
        pos = place_via_near_point(it['x'], it['y'], net)
        if pos:
            # if it's a pad and via is outside pad, route short track
            pad_info = pad_of(it)
            if pad_info:
                fp, p, rect = pad_info
                cx=(rect[0]+rect[2])/2.0; cy=(rect[1]+rect[3])/2.0
                # if via outside pad, add track from pad center to via
                # determine layer from pad
                layer = pcbnew.F_Cu if 'F.Cu' in it['layer_raw'] else pcbnew.B_Cu
                obs = f_obs if layer==pcbnew.F_Cu else b_obs
                if short_track_to_via(cx, cy, pos[0], pos[1], layer, 0.5, net, obs):
                    added_tracks+=1
            if add_via(pos[0], pos[1], net):
                added_vias+=1
                pts.append(pos)
            else:
                pts.append(None)
        else:
            pts.append(None)
    # If both vias placed and still likely disconnected, try B track between them
    if pts[0] and pts[1]:
        # Only add a track if B.Cu track clear; if not, rely on plane
        if b_obs.track_clear(pts[0][0], pts[0][1], pts[1][0], pts[1][1], 0.5, net.GetNetname()):
            add_track(pts[0][0], pts[0][1], pts[1][0], pts[1][1], pcbnew.B_Cu, 0.5, net, b_obs)
            added_tracks+=1

for z in brd.Zones():
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
filler = pcbnew.ZONE_FILLER(brd)
filler.Fill(brd.Zones())
brd.BuildConnectivity()
pcbnew.SaveBoard(BOARD_PATH, brd)
print(f'added vias {added_vias}, tracks {added_tracks}, skipped {skipped}')
