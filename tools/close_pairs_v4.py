#!/usr/bin/env python3
"""Close short unconnected pairs with netclass-aware clearance/width and board cutout checks."""
import re, math, pcbnew
MM = 1_000_000
BOARD_PATH = '/workspace/kicad/nebula_qshield.kicad_pcb'
DRC_PATH = '/workspace/nebula_qshield-drc.rpt'

# Board outline parameters (rounded rectangle)
BOARD_LEFT = -8.0
BOARD_RIGHT = 142.0
BOARD_BOTTOM = -2.0
BOARD_TOP = 118.0
BOARD_CORNER_R = 2.5
EDGE_MARGIN = 0.25

# Internal rectangular cutouts (left,bottom,right,top)
CUTOUTS = [(2.08, 81.56, 22.5, 94.56), (60.08, 88.56, 77.08, 94.56)]

brd = pcbnew.LoadBoard(BOARD_PATH)

NET_CLASSES = {}
all_nets = list(brd.GetNetsByName().values()) if hasattr(brd, 'GetNetsByName') else []
for net in brd.GetNetsByName().values():
    NET_CLASSES[net.GetNetname()] = [c.strip() for c in net.GetNetClassName().split(',')]

def netclasses(name):
    return NET_CLASSES.get(name, ['Default'])

def track_width_for_net(name):
    cls = netclasses(name)
    if 'RelayHV' in cls:
        return 1.0
    if 'HighCurrent' in cls or 'Power' in cls:
        return 0.5
    return 0.25

def via_size_for_net(name):
    cls = netclasses(name)
    if 'RelayHV' in cls:
        return (1.0, 0.5)
    if 'Analog' in cls:
        return (0.6, 0.3)
    return (0.5, 0.2)

def clearance_between(n1, n2):
    cls1 = netclasses(n1); cls2 = netclasses(n2)
    if 'RelayHV' in cls1 or 'RelayHV' in cls2:
        return 0.60  # extra margin
    if 'Analog' in cls1 or 'Analog' in cls2:
        return 0.35
    if 'Power' in cls1 or 'Power' in cls2 or 'HighCurrent' in cls1 or 'HighCurrent' in cls2:
        return 0.30
    return 0.25

def parse_layer(s):
    s = s.strip()
    return ('F.Cu' in s, 'B.Cu' in s)

def get_pad_rect(p):
    bb = p.GetBoundingBox()
    return (bb.GetX()/MM, bb.GetY()/MM, (bb.GetX()+bb.GetWidth())/MM, (bb.GetY()+bb.GetHeight())/MM)

def seg_to_seg_dist(x1,y1,x2,y2,x3,y3,x4,y4):
    def orient(ax,ay,bx,by,cx,cy): return (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
    def on_seg(ax,ay,bx,by,cx,cy): return min(ax,bx)-1e-9<=cx<=max(ax,bx)+1e-9 and min(ay,by)-1e-9<=cy<=max(ay,by)+1e-9
    def intersect():
        o1=orient(x1,y1,x2,y2,x3,y3); o2=orient(x1,y1,x2,y2,x4,y4)
        o3=orient(x3,y3,x4,y4,x1,y1); o4=orient(x3,y3,x4,y4,x2,y2)
        if o1==0 and on_seg(x1,y1,x2,y2,x3,y3): return True
        if o2==0 and on_seg(x1,y1,x2,y2,x4,y4): return True
        if o3==0 and on_seg(x3,y3,x4,y4,x1,y1): return True
        if o4==0 and on_seg(x3,y3,x4,y4,x2,y2): return True
        return (o1>0)!=(o2>0) and (o3>0)!=(o4>0)
    if intersect(): return 0.0
    def sdp(px,py,ax,ay,bx,by):
        dx=bx-ax; dy=by-ay; l2=dx*dx+dy*dy
        if l2==0: return math.hypot(px-ax,py-ay)
        t=max(0.0,min(1.0,((px-ax)*dx+(py-ay)*dy)/l2))
        return math.hypot(px-(ax+t*dx), py-(ay+t*dy))
    return min(sdp(x1,y1,x3,y3,x4,y4), sdp(x2,y2,x3,y3,x4,y4), sdp(x3,y3,x1,y1,x2,y2), sdp(x4,y4,x1,y1,x2,y2))

def seg_dist_to_point(px,py,ax,ay,bx,by):
    dx=bx-ax; dy=by-ay; l2=dx*dx+dy*dy
    if l2==0: return math.hypot(px-ax,py-ay)
    t=max(0.0,min(1.0,((px-ax)*dx+(py-ay)*dy)/l2))
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))

def rect_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2):
    dmin=float('inf')
    for a,b,c,d in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]:
        dmin=min(dmin, seg_to_seg_dist(a,b,c,d,sx1,sy1,sx2,sy2))
    return dmin

def rect_dist(px,py,rect):
    x1,y1,x2,y2=rect
    dx=max(max(x1-px,0.0),px-x2); dy=max(max(y1-py,0.0),py-y2)
    return math.hypot(dx,dy)

# Rounded-rectangle geometry helpers

def point_in_rounded_rect(px,py,left,bottom,right,top,r):
    """Point inside rounded rectangle (edges straight, corners cut as arcs radius r)."""
    if not (left <= px <= right and bottom <= py <= top):
        return False
    # check corner disks (outside rectangle) for the four corners
    centers = [(left+r, bottom+r), (right-r, bottom+r), (left+r, top-r), (right-r, top-r)]
    for cx,cy in centers:
        if px < cx and py < cy and math.hypot(px-cx, py-cy) < r:
            return False
        if px > cx and py < cy and math.hypot(px-cx, py-cy) < r:
            return False
        if px < cx and py > cy and math.hypot(px-cx, py-cy) < r:
            return False
        if px > cx and py > cy and math.hypot(px-cx, py-cy) < r:
            return False
    return True

def point_on_board(px,py,margin=0.0):
    return point_in_rounded_rect(px,py, BOARD_LEFT+margin, BOARD_BOTTOM+margin, BOARD_RIGHT-margin, BOARD_TOP-margin, BOARD_CORNER_R+margin)

def segment_in_board(x1,y1,x2,y2,width):
    # sample along segment
    samples = 10
    margin = EDGE_MARGIN + width/2.0
    for i in range(samples+1):
        t=i/samples
        x=x1+(x2-x1)*t; y=y1+(y2-y1)*t
        if not point_on_board(x,y,margin):
            return False
    return True

def segment_clear_of_cutouts(x1,y1,x2,y2,width):
    # For each cutout, the copper edge must stay at least EDGE_MARGIN away.
    # Conservatively reject if the segment gets within (margin + width/2) of the cutout rectangle (Minkowski square approximation).
    hw = width/2.0
    for cl,cb,cr,ct in CUTOUTS:
        margin = EDGE_MARGIN + hw
        # expanded rectangle (square, ignoring corner rounding)
        el, eb, er, et = cl-margin, cb-margin, cr+margin, ct+margin
        # Check if any sample point is inside expanded rectangle
        samples = 10
        for i in range(samples+1):
            t=i/samples
            x=x1+(x2-x1)*t; y=y1+(y2-y1)*t
            if el <= x <= er and eb <= y <= et:
                return False
        # Also check if the segment intersects the expanded rectangle edges (conservative)
        if rect_to_seg_dist(el,eb,er,et,x1,y1,x2,y2) < 1e-6:
            return False
    return True

class ObstacleSet:
    def __init__(self, brd, layer_id):
        self.layer = layer_id
        self.vias=[]; self.tracks=[]; self.pads=[]
        for t in brd.GetTracks():
            if isinstance(t, pcbnew.PCB_VIA):
                if not t.GetLayerSet().Contains(layer_id): continue
                r=t.GetWidth(layer_id)/2.0/MM
                pos=t.GetPosition()
                self.vias.append((pos.x/MM, pos.y/MM, r, t.GetNetname()))
            elif isinstance(t, pcbnew.PCB_TRACK):
                if t.GetLayer()!=layer_id: continue
                r=t.GetWidth()/2.0/MM
                s=t.GetStart(); e=t.GetEnd()
                self.tracks.append((s.x/MM, s.y/MM, e.x/MM, e.y/MM, r, t.GetNetname()))
        for fp in brd.GetFootprints():
            for p in fp.Pads():
                if not p.GetLayerSet().Contains(layer_id): continue
                rect=get_pad_rect(p)
                self.pads.append((rect[0],rect[1],rect[2],rect[3],p.GetNetname()))

    def track_clear(self, x1,y1,x2,y2,width,net):
        hw=width/2.0
        # Board edge and cutouts
        if not segment_in_board(x1,y1,x2,y2,width): return False
        if not segment_clear_of_cutouts(x1,y1,x2,y2,width): return False
        for vx,vy,r,n in self.vias:
            if n==net: continue
            d=seg_dist_to_point(vx,vy,x1,y1,x2,y2)
            if d - r - hw - clearance_between(net,n) < -0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            d=seg_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2)
            if d - r - hw - clearance_between(net,n) < -0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            d=rect_to_seg_dist(px1,py1,px2,py2,x1,y1,x2,y2)
            if d - hw - clearance_between(net,n) < -0.001: return False
        return True

    def point_safe(self, x, y, radius, net):
        if not point_on_board(x,y, EDGE_MARGIN + radius): return False
        # check cutouts
        for cl,cb,cr,ct in CUTOUTS:
            margin = EDGE_MARGIN + radius
            if cl-margin <= x <= cr+margin and cb-margin <= y <= ct+margin:
                return False
        for vx,vy,r,n in self.vias:
            if n==net: continue
            if math.hypot(x-vx,y-vy) - r - radius - clearance_between(net,n) < -0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            d=seg_dist_to_point(x,y,sx1,sy1,sx2,sy2)
            if d - r - radius - clearance_between(net,n) < -0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            d=rect_dist(x,y,(px1,py1,px2,py2))
            if d - radius - clearance_between(net,n) < -0.001: return False
        return True

    def add_track(self, x1,y1,x2,y2,width,net):
        self.tracks.append((x1,y1,x2,y2,width/2.0,net))
    def add_via(self, x,y,r,net):
        self.vias.append((x,y,r,net))

def add_track_obj(x1,y1,x2,y2,layer_id,width,net):
    t=pcbnew.PCB_TRACK(brd)
    t.SetStart(pcbnew.VECTOR2I(int(round(x1*MM)),int(round(y1*MM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(x2*MM)),int(round(y2*MM))))
    t.SetLayer(layer_id)
    t.SetWidth(int(round(width*MM)))
    t.SetNet(net)
    brd.Add(t)

def add_via_obj(x,y,vd,drill,net):
    v=pcbnew.PCB_VIA(brd)
    v.SetPosition(pcbnew.VECTOR2I(int(round(x*MM)),int(round(y*MM))))
    v.SetNet(net)
    v.SetWidth(int(round(vd*MM)))
    v.SetDrill(int(round(drill*MM)))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetRemoveUnconnected(False)
    brd.Add(v)

def add_routed_track(pts, layer_id, width, net, obs):
    if len(pts) < 2: return False
    for i in range(len(pts)-1):
        x1,y1=pts[i]; x2,y2=pts[i+1]
        if math.hypot(x1-x2,y1-y2) < 0.01: continue
        if not obs.track_clear(x1,y1,x2,y2,width,net.GetNetname()):
            return False
    for i in range(len(pts)-1):
        x1,y1=pts[i]; x2,y2=pts[i+1]
        if math.hypot(x1-x2,y1-y2) < 0.01: continue
        add_track_obj(x1,y1,x2,y2,layer_id,width,net)
        obs.add_track(x1,y1,x2,y2,width,net.GetNetname())
    return True

# Parse DRC pairs
text=open(DRC_PATH).read()
blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    for line in block.split('\n'):
        m=re.match(r'\s+@\(([-\d\.]+) mm, ([-\d\.]+) mm\): (Pad \d+|Track|Via) \[([^\]]+)\](?: of ([^\n]+?))? on ([\w\. \-]+)', line)
        if m:
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer_raw':m.group(6).strip()})
    if len(items)==2:
        pairs.append(items)

print('parsed pairs', len(pairs))

pad_by_ref={}
for fp in brd.GetFootprints():
    for p in fp.Pads():
        pad_by_ref[(fp.GetReference(), str(p.GetNumber()))] = (fp, p, get_pad_rect(p))

def pad_of(it):
    if 'Pad ' in it['type']:
        return pad_by_ref.get((it['ref'], it['type'].split()[-1]))
    return None

f_obs=ObstacleSet(brd, pcbnew.F_Cu)
b_obs=ObstacleSet(brd, pcbnew.B_Cu)
obs_map={pcbnew.F_Cu:f_obs, pcbnew.B_Cu:b_obs}

def layers_for(it1, it2):
    l1=parse_layer(it1['layer_raw']); l2=parse_layer(it2['layer_raw'])
    res=[]
    if l1[0] and l2[0]: res.append(pcbnew.F_Cu)
    if l1[1] and l2[1]: res.append(pcbnew.B_Cu)
    return res

def candidate_corners(x1,y1,x2,y2):
    offs=[0]
    for o in [-2.0,-1.5,-1.0,-0.75,-0.5,-0.25,0.25,0.5,0.75,1.0,1.5,2.0]:
        offs.append(o)
    midx=(x1+x2)/2.0; midy=(y1+y2)/2.0
    cand=[]
    for ox in offs:
        for oy in offs:
            cand.append((x1+ox, y2+oy))
            cand.append((x2+ox, y1+oy))
            cand.append((midx+ox, y1+oy))
            cand.append((midx+ox, y2+oy))
            cand.append((x1+ox, midy+oy))
            cand.append((x2+ox, midy+oy))
            cand.append((midx+ox, midy+oy))
    return cand

def u_shape_corners(x1,y1,x2,y2):
    offs=[0]
    for o in [-2.0,-1.5,-1.0,-0.75,-0.5,-0.25,0.25,0.5,0.75,1.0,1.5,2.0]:
        offs.append(o)
    cand=[]
    for o in offs:
        cand.append((x1+o, y1, x1+o, y2))
        cand.append((x2+o, y1, x2+o, y2))
        cand.append((x1, y1+o, x2, y1+o))
        cand.append((x1, y2+o, x2, y2+o))
    return cand

def try_same_layer(it1, it2, layer_id, net):
    x1,y1=it1['x'],it1['y']; x2,y2=it2['x'],it2['y']
    if math.hypot(x1-x2,y1-y2) < 0.01: return False
    width=track_width_for_net(net.GetNetname())
    obs=obs_map[layer_id]
    # straight
    if add_routed_track([(x1,y1),(x2,y2)], layer_id, width, net, obs): return True
    # L-shape 2 segments
    for cx,cy in candidate_corners(x1,y1,x2,y2):
        if add_routed_track([(x1,y1),(cx,cy),(x2,y2)], layer_id, width, net, obs): return True
    # U-shape 3 segments
    for x1a,y1a,x2a,y2a in u_shape_corners(x1,y1,x2,y2):
        if add_routed_track([(x1,y1),(x1a,y1a),(x2a,y2a),(x2,y2)], layer_id, width, net, obs): return True
    return False

def place_via_at_pad(it, net):
    info=pad_of(it)
    if not info: return None
    fp,p,rect=info
    cx=(rect[0]+rect[2])/2.0; cy=(rect[1]+rect[3])/2.0
    vd,drill=via_size_for_net(net.GetNetname())
    vr=vd/2.0
    for dx in [0,0.1,-0.1,0.2,-0.2,0.3,-0.3,0.4,-0.4,0.5,-0.5]:
        for dy in [0,0.1,-0.1,0.2,-0.2,0.3,-0.3,0.4,-0.4,0.5,-0.5]:
            px,py=cx+dx,cy+dy
            # via body must fit inside pad (smaller margin ok)
            if not (rect[0]+vr <= px <= rect[2]-vr and rect[1]+vr <= py <= rect[3]-vr):
                continue
            # plus other obstacles
            if f_obs.point_safe(px,py,vr,net.GetNetname()) and b_obs.point_safe(px,py,vr,net.GetNetname()):
                return (px,py,vd,drill,(cx,cy))
    return None

def find_safe_via_point(x,y,net):
    vd,drill=via_size_for_net(net.GetNetname())
    vr=vd/2.0
    # start at current point if safe
    if f_obs.point_safe(x,y,vr,net.GetNetname()) and b_obs.point_safe(x,y,vr,net.GetNetname()):
        return (x,y,vd,drill)
    for r in [0.25,0.5,0.75,1.0,1.25,1.5,2.0,2.5,3.0,3.5,4.0]:
        n=max(8, int(r*16))
        for i in range(n):
            ang=2*math.pi*i/n
            px=x+r*math.cos(ang); py=y+r*math.sin(ang)
            if f_obs.point_safe(px,py,vr,net.GetNetname()) and b_obs.point_safe(px,py,vr,net.GetNetname()):
                return (px,py,vd,drill)
    return None

def try_via_bridge(it1, it2, net):
    # prefer F side for via and B side for connecting if one endpoint is on B
    l1=parse_layer(it1['layer_raw']); l2=parse_layer(it2['layer_raw'])
    width=track_width_for_net(net.GetNetname())
    pts=[]
    for it in [it1,it2]:
        info=pad_of(it); pad_center=None
        if info:
            fp,p,rect=info
            pad_center=((rect[0]+rect[2])/2.0, (rect[1]+rect[3])/2.0)
            res=place_via_at_pad(it, net)
            if res:
                px,py,vd,drill,_=res
                add_via_obj(px,py,vd,drill,net)
                f_obs.add_via(px,py,vd/2.0,net.GetNetname()); b_obs.add_via(px,py,vd/2.0,net.GetNetname())
                pts.append((px,py,pad_center))
                continue
        # fallback: safe near endpoint
        ptx,pty=it['x'],it['y']
        if pad_center: ptx,pty=pad_center
        safe=find_safe_via_point(ptx,pty,net)
        if not safe:
            return False
        vx,vy,vd,drill=safe
        # route short track from endpoint to via on a layer this endpoint can use
        if parse_layer(it['layer_raw'])[0]:
            layer=pcbnew.F_Cu; obs=f_obs
        elif parse_layer(it['layer_raw'])[1]:
            layer=pcbnew.B_Cu; obs=b_obs
        else:
            layer=pcbnew.F_Cu; obs=f_obs
        if not add_routed_track([(ptx,pty),(vx,vy)], layer, width, net, obs):
            return False
        pts.append((vx,vy,(ptx,pty)))
    if len(pts)!=2: return False
    # Try to connect the two vias on B.Cu with straight or L
    if b_obs.track_clear(pts[0][0],pts[0][1],pts[1][0],pts[1][1],width,net.GetNetname()):
        add_routed_track([(pts[0][0],pts[0][1]),(pts[1][0],pts[1][1])], pcbnew.B_Cu, width, net, b_obs)
        return True
    for cx,cy in candidate_corners(pts[0][0],pts[0][1],pts[1][0],pts[1][1]):
        if add_routed_track([(pts[0][0],pts[0][1]),(cx,cy),(pts[1][0],pts[1][1])], pcbnew.B_Cu, width, net, b_obs):
            return True
    return False

# Process shortest first
pair_data=[]
for p in pairs:
    d=math.hypot(p[0]['x']-p[1]['x'], p[0]['y']-p[1]['y'])
    pair_data.append((d,p))
pair_data.sort(key=lambda x:x[0])

added=0; skipped=0; via_bridges=0
for d,p in pair_data:
    it1,it2=p
    if it1['net']!=it2['net']:
        skipped+=1; continue
    net=brd.FindNet(it1['net'])
    if net is None:
        skipped+=1; continue
    done=False
    for layer in layers_for(it1,it2):
        if try_same_layer(it1,it2,layer,net):
            added+=1; done=True; break
    if done: continue
    if try_via_bridge(it1,it2,net):
        added+=1; via_bridges+=1; continue
    skipped+=1

print('added tracks', added, 'via bridges', via_bridges, 'skipped', skipped)

for z in brd.Zones():
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
filler=pcbnew.ZONE_FILLER(brd)
filler.Fill(brd.Zones())
brd.BuildConnectivity()
pcbnew.SaveBoard(BOARD_PATH, brd)
print('Saved')
