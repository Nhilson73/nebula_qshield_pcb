#!/usr/bin/env python3
import re, math, pcbnew

MM = 1_000_000
BOARD_PATH = '/workspace/kicad/nebula_qshield.kicad_pcb'
DRC_PATH = '/workspace/nebula_qshield-drc.rpt'

brd = pcbnew.LoadBoard(BOARD_PATH)

def get_pad_rect(p):
    bb = p.GetBoundingBox()
    return (bb.GetX() / MM, bb.GetY() / MM, (bb.GetX() + bb.GetWidth()) / MM, (bb.GetY() + bb.GetHeight()) / MM)

def parse_layer(s):
    s = s.strip()
    if 'F.Cu' in s and 'B.Cu' in s:
        return ('F.Cu','B.Cu')
    return (s,)

def netclass_clearance(netname, other_net):
    if 'Analog' in netname or 'Analog' in other_net:
        return 0.30
    if netname in ('/I2C_SDA','/I2C_SCL') or other_net in ('/I2C_SDA','/I2C_SCL'):
        return 0.25
    if any(s in netname or s in other_net for s in ['/12V','/5V','/3V3','VIN_12V','12V_FUSED','CHILLER','MOTOR','COIL','/Actuator Drivers']):
        return 0.30
    if 'Relay' in netname or 'Relay' in other_net:
        return 0.50
    return 0.20

def track_width_for_net(netname):
    if any(s in netname for s in ['/12V','/5V','/3V3','CHILLER','MOTOR','COIL','VIN','12V_FUSED']):
        return 0.50
    return 0.25

# segment geometry
def orient(ax, ay, bx, by, cx, cy):
    return (bx-ax)*(cy-ay) - (by-ay)*(cx-ax)

def on_seg(ax, ay, bx, by, cx, cy):
    return min(ax,bx) <= cx <= max(ax,bx) and min(ay,by) <= cy <= max(ay,by)

def segments_intersect(x1,y1,x2,y2,x3,y3,x4,y4):
    o1 = orient(x1,y1,x2,y2,x3,y3)
    o2 = orient(x1,y1,x2,y2,x4,y4)
    o3 = orient(x3,y3,x4,y4,x1,y1)
    o4 = orient(x3,y3,x4,y4,x2,y2)
    if o1==0 and on_seg(x1,y1,x2,y2,x3,y3): return True
    if o2==0 and on_seg(x1,y1,x2,y2,x4,y4): return True
    if o3==0 and on_seg(x3,y3,x4,y4,x1,y1): return True
    if o4==0 and on_seg(x3,y3,x4,y4,x2,y2): return True
    return (o1>0) != (o2>0) and (o3>0) != (o4>0)

def seg_to_seg_dist(x1,y1,x2,y2,x3,y3,x4,y4):
    if segments_intersect(x1,y1,x2,y2,x3,y3,x4,y4):
        return 0.0
    def seg_dist_point(px,py,ax,ay,bx,by):
        dx=bx-ax; dy=by-ay
        l2=dx*dx+dy*dy
        if l2==0:
            return math.hypot(px-ax,py-ay)
        t=max(0.0,min(1.0,((px-ax)*dx+(py-ay)*dy)/l2))
        cx=ax+t*dx; cy=ay+t*dy
        return math.hypot(px-cx,py-cy)
    return min(
        seg_dist_point(x1,y1,x3,y3,x4,y4),
        seg_dist_point(x2,y2,x3,y3,x4,y4),
        seg_dist_point(x3,y3,x1,y1,x2,y2),
        seg_dist_point(x4,y4,x1,y1,x2,y2),
    )

def seg_dist_to_point(px,py,ax,ay,bx,by):
    dx=bx-ax; dy=by-ay
    l2=dx*dx+dy*dy
    if l2==0:
        return math.hypot(px-ax,py-ay)
    t=max(0.0,min(1.0,((px-ax)*dx+(py-ay)*dy)/l2))
    cx=ax+t*dx; cy=ay+t*dy
    return math.hypot(px-cx,py-cy)

def rect_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2):
    sides=[(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]
    dmin=float('inf')
    for a,b,c,d in sides:
        dmin=min(dmin, seg_to_seg_dist(a,b,c,d,sx1,sy1,sx2,sy2))
    return dmin

class ObstacleSet:
    def __init__(self, brd, layer_id):
        self.vias=[]; self.tracks=[]; self.pads=[]; self.edges=[]
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
        for d in brd.GetDrawings():
            if d.GetLayer()==pcbnew.Edge_Cuts and hasattr(d,'GetStart'):
                s=d.GetStart(); e=d.GetEnd()
                self.edges.append((s.x/MM,s.y/MM,e.x/MM,e.y/MM))

    def track_clear(self, x1,y1,x2,y2,width,net):
        hw=width/2.0
        for (vx,vy,r,n) in self.vias:
            if n==net: continue
            d=seg_dist_to_point(vx,vy,x1,y1,x2,y2)
            if d - r - hw - netclass_clearance(net,n) < -0.001:
                return False
        for (sx1,sy1,sx2,sy2,r,n) in self.tracks:
            if n==net: continue
            d=seg_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2)
            if d - r - hw - netclass_clearance(net,n) < -0.001:
                return False
        for (px1,py1,px2,py2,n) in self.pads:
            if n==net: continue
            d=rect_to_seg_dist(px1,py1,px2,py2,x1,y1,x2,y2)
            if d - hw - netclass_clearance(net,n) < -0.001:
                return False
        for (ex1,ey1,ex2,ey2) in self.edges:
            d=seg_to_seg_dist(x1,y1,x2,y2,ex1,ey1,ex2,ey2)
            if d - hw - 0.25 < -0.001:
                return False
        return True

    def add_track(self, x1,y1,x2,y2,width,net):
        r=width/2.0
        self.tracks.append((x1,y1,x2,y2,r,net))

def add_track_obj(x1,y1,x2,y2,layer_id,width,net):
    t=pcbnew.PCB_TRACK(brd)
    t.SetStart(pcbnew.VECTOR2I(int(round(x1*MM)),int(round(y1*MM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(x2*MM)),int(round(y2*MM))))
    t.SetLayer(layer_id)
    t.SetWidth(int(round(width*MM)))
    t.SetNet(net)
    brd.Add(t)

def try_connect(it1, it2, obs_map, net):
    l1=parse_layer(it1['layer_raw']); l2=parse_layer(it2['layer_raw'])
    width=track_width_for_net(it1['net'])
    # If both on same copper layer (or one is via on F/B and other on F)
    layers=[]
    if 'F.Cu' in l1 and 'F.Cu' in l2: layers.append(pcbnew.F_Cu)
    if 'B.Cu' in l1 and 'B.Cu' in l2: layers.append(pcbnew.B_Cu)
    # if one is a via, we can connect on the other item's layer
    if 'F.Cu - B.Cu' in it1['layer_raw'] and 'F.Cu' in l2:
        if pcbnew.F_Cu not in layers: layers.append(pcbnew.F_Cu)
    if 'F.Cu - B.Cu' in it2['layer_raw'] and 'F.Cu' in l1:
        if pcbnew.F_Cu not in layers: layers.append(pcbnew.F_Cu)
    x1,y1=it1['x'],it1['y']; x2,y2=it2['x'],it2['y']
    for layer_id in layers:
        obs=obs_map[layer_id]
        # straight
        if obs.track_clear(x1,y1,x2,y2,width,it1['net']):
            add_track_obj(x1,y1,x2,y2,layer_id,width,net)
            obs.add_track(x1,y1,x2,y2,width,it1['net'])
            return True
        # L-shape via midpoint candidates
        mx1=(x1+x2)/2.0
        # try horizontal then vertical
        for mx in [mx1]:
            for my in [y1,y2,(y1+y2)/2.0]:
                if obs.track_clear(x1,y1,mx,my,width,it1['net']) and obs.track_clear(mx,my,x2,y2,width,it1['net']):
                    # check corner clearance? each segment checked; corner point only needs to not short; it is a vertex inside obs? track_clear uses segment distance, a point at a via/pad center would be within radius but segment distance from a point to a segment is 0 if point on segment? Actually if mx,my is inside a pad, the segment passes through pad. track_clear rect_to_seg_dist returns 0 because segment intersects pad side. Good.
                    add_track_obj(x1,y1,mx,my,layer_id,width,net)
                    add_track_obj(mx,my,x2,y2,layer_id,width,net)
                    obs.add_track(x1,y1,mx,my,width,it1['net'])
                    obs.add_track(mx,my,x2,y2,width,it1['net'])
                    return True
    return False

# parse DRC pairs
text=open(DRC_PATH).read()
blocks=[]
for m in re.finditer(r'\[unconnected_items\]: Missing connection between items', text):
    start=m.start()
    end=text.find('\n[', start+1)
    if end==-1: end=len(text)
    blocks.append(text[start:end])

pairs=[]
for block in blocks:
    items=[]
    for line in block.split('\n'):
        m=re.match(r'\s+@\(([-\d\.]+) mm, ([-\d\.]+) mm\): (Pad \d+|Track|Via) \[([^\]]+)\](?: of ([^\n]+?))? on ([\w\. \-]+)', line)
        if m:
            items.append({
                'x':float(m.group(1)), 'y':float(m.group(2)),
                'type':m.group(3), 'net':m.group(4),
                'ref':m.group(5), 'layer_raw':m.group(6).strip()
            })
    if len(items)==2:
        pairs.append(items)

print('parsed pairs', len(pairs))
# group by net, sort by distance
pair_data=[]
for p in pairs:
    d=math.hypot(p[0]['x']-p[1]['x'], p[0]['y']-p[1]['y'])
    pair_data.append((d,p))
pair_data.sort(key=lambda x:x[0])

# prepare obstacle sets for both layers
obs_map={pcbnew.F_Cu: ObstacleSet(brd, pcbnew.F_Cu), pcbnew.B_Cu: ObstacleSet(brd, pcbnew.B_Cu)}

added=0; skipped=0
for d,p in pair_data:
    it1,it2=p
    if it1['net']!=it2['net']:
        continue
    # skip power/motor nets for now? handle all
    net=brd.FindNet(it1['net'])
    if net is None:
        continue
    if try_connect(it1,it2,obs_map,net):
        added+=1
    else:
        skipped+=1

print('added', added, 'skipped', skipped)
for z in brd.Zones():
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
filler=pcbnew.ZONE_FILLER(brd)
filler.Fill(brd.Zones())
brd.BuildConnectivity()
pcbnew.SaveBoard(BOARD_PATH, brd)
print('Saved')
