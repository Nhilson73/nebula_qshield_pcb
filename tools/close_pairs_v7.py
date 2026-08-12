#!/usr/bin/env python3
"""Close short unconnected pairs v6: plane-net via-only and improved signal routing."""
import re, math, pcbnew
MM=1_000_000
BOARD_PATH='/workspace/kicad/nebula_qshield.kicad_pcb'
DRC_PATH='/workspace/kicad/nebula_qshield-drc.rpt'

BOARD_LEFT=-8.0; BOARD_RIGHT=142.0; BOARD_BOTTOM=-2.0; BOARD_TOP=118.0; BOARD_CORNER_R=2.5
EDGE_MARGIN=0.25
CUTOUTS=[(2.08,81.56,22.5,94.56),(60.08,88.56,77.08,94.56)]
PLANE_NETS={'GND','/12V_RAIL','/5V_RAIL','/3V3_RAIL'}

brd=pcbnew.LoadBoard(BOARD_PATH)
NET_CLASSES={}
for net in brd.GetNetsByName().values():
    NET_CLASSES[net.GetNetname()]=[c.strip() for c in net.GetNetClassName().split(',')]

def netclasses(name): return NET_CLASSES.get(name,['Default'])
def track_width(name):
    c=netclasses(name)
    return 1.0 if 'RelayHV' in c else 0.5 if 'HighCurrent' in c or 'Power' in c else 0.25
def via_size(name):
    c=netclasses(name)
    return (1.0,0.5) if 'RelayHV' in c else (0.6,0.3) if 'Analog' in c else (0.5,0.2)
def clearance(n1,n2):
    c1=netclasses(n1); c2=netclasses(n2)
    if 'RelayHV' in c1 or 'RelayHV' in c2: return 0.60
    if 'Analog' in c1 or 'Analog' in c2: return 0.35
    if 'Power' in c1 or 'Power' in c2 or 'HighCurrent' in c1 or 'HighCurrent' in c2: return 0.30
    return 0.25

def get_pad_rect(p):
    bb=p.GetBoundingBox(); return (bb.GetX()/MM, bb.GetY()/MM, (bb.GetX()+bb.GetWidth())/MM, (bb.GetY()+bb.GetHeight())/MM)

def point_on_board(px,py,margin=0.0):
    if not (BOARD_LEFT+margin<=px<=BOARD_RIGHT-margin and BOARD_BOTTOM+margin<=py<=BOARD_TOP-margin): return False
    centers=[(BOARD_LEFT+BOARD_CORNER_R,BOARD_BOTTOM+BOARD_CORNER_R),(BOARD_RIGHT-BOARD_CORNER_R,BOARD_BOTTOM+BOARD_CORNER_R),(BOARD_LEFT+BOARD_CORNER_R,BOARD_TOP-BOARD_CORNER_R),(BOARD_RIGHT-BOARD_CORNER_R,BOARD_TOP-BOARD_CORNER_R)]
    for cx,cy in centers:
        if ((px<cx and py<cy) or (px>cx and py<cy) or (px<cx and py>cy) or (px>cx and py>cy)) and math.hypot(px-cx,py-cy)<BOARD_CORNER_R+margin: return False
    return True

def segment_in_board(x1,y1,x2,y2,w):
    for i in range(11):
        t=i/10; x=x1+(x2-x1)*t; y=y1+(y2-y1)*t
        if not point_on_board(x,y,EDGE_MARGIN+w/2): return False
    return True

def rect_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2):
    dmin=float('inf')
    for a,b,c,d in [(x1,y1,x2,y1),(x2,y1,x2,y2),(x2,y2,x1,y2),(x1,y2,x1,y1)]:
        dmin=min(dmin, seg_to_seg_dist(a,b,c,d,sx1,sy1,sx2,sy2))
    return dmin

def seg_to_seg_dist(x1,y1,x2,y2,x3,y3,x4,y4):
    def orient(ax,ay,bx,by,cx,cy): return (bx-ax)*(cy-ay)-(by-ay)*(cx-ax)
    def onseg(ax,ay,bx,by,cx,cy): return min(ax,bx)-1e-9<=cx<=max(ax,bx)+1e-9 and min(ay,by)-1e-9<=cy<=max(ay,by)+1e-9
    def intersect():
        o1=orient(x1,y1,x2,y2,x3,y3); o2=orient(x1,y1,x2,y2,x4,y4)
        o3=orient(x3,y3,x4,y4,x1,y1); o4=orient(x3,y3,x4,y4,x2,y2)
        if o1==0 and onseg(x1,y1,x2,y2,x3,y3): return True
        if o2==0 and onseg(x1,y1,x2,y2,x4,y4): return True
        if o3==0 and onseg(x3,y3,x4,y4,x1,y1): return True
        if o4==0 and onseg(x3,y3,x4,y4,x2,y2): return True
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

def rect_point_dist(px,py,rect):
    x1,y1,x2,y2=rect
    dx=max(max(x1-px,0.0),px-x2); dy=max(max(y1-py,0.0),py-y2)
    return math.hypot(dx,dy)

def point_in_pad(px,py,rect,margin=0.0):
    return rect[0]-margin<=px<=rect[2]+margin and rect[1]-margin<=py<=rect[3]+margin

def segment_clear_cutouts(x1,y1,x2,y2,w):
    for cl,cb,cr,ct in CUTOUTS:
        m=EDGE_MARGIN+w/2
        el,eb,er,et=cl-m,cb-m,cr+m,ct+m
        for i in range(11):
            t=i/10; x=x1+(x2-x1)*t; y=y1+(y2-y1)*t
            if el<=x<=er and eb<=y<=et: return False
        if rect_seg_dist(el,eb,er,et,x1,y1,x2,y2)<1e-6: return False
    return True

class ObstacleSet:
    def __init__(self, brd, layer_id):
        self.layer=layer_id; self.vias=[]; self.tracks=[]; self.pads=[]
        for t in brd.GetTracks():
            if isinstance(t, pcbnew.PCB_VIA):
                if not t.GetLayerSet().Contains(layer_id): continue
                r=t.GetWidth(layer_id)/2.0/MM; pos=t.GetPosition()
                self.vias.append((pos.x/MM,pos.y/MM,r,t.GetNetname()))
            elif isinstance(t, pcbnew.PCB_TRACK):
                if t.GetLayer()!=layer_id: continue
                r=t.GetWidth()/2.0/MM; s=t.GetStart(); e=t.GetEnd()
                self.tracks.append((s.x/MM,s.y/MM,e.x/MM,e.y/MM,r,t.GetNetname()))
        for fp in brd.GetFootprints():
            for p in fp.Pads():
                if not p.GetLayerSet().Contains(layer_id): continue
                rect=get_pad_rect(p)
                self.pads.append((rect[0],rect[1],rect[2],rect[3],p.GetNetname()))
    def track_clear(self,x1,y1,x2,y2,w,net):
        hw=w/2.0
        if not segment_in_board(x1,y1,x2,y2,w) or not segment_clear_cutouts(x1,y1,x2,y2,w): return False
        for vx,vy,r,n in self.vias:
            if n==net: continue
            d=seg_dist_to_point(vx,vy,x1,y1,x2,y2)
            if d - r - hw - clearance(net,n) < -0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            d=seg_to_seg_dist(x1,y1,x2,y2,sx1,sy1,sx2,sy2)
            if d - r - hw - clearance(net,n) < -0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            d=rect_seg_dist(px1,py1,px2,py2,x1,y1,x2,y2)
            if d - hw - clearance(net,n) < -0.001: return False
        return True
    def point_safe(self,x,y,r,net):
        if not point_on_board(x,y,EDGE_MARGIN+r): return False
        for cl,cb,cr,ct in CUTOUTS:
            m=EDGE_MARGIN+r
            if cl-m<=x<=cr+m and cb-m<=y<=ct+m: return False
        for vx,vy,rr,n in self.vias:
            if n==net: continue
            if math.hypot(x-vx,y-vy)-rr-r-clearance(net,n)<-0.001: return False
        for sx1,sy1,sx2,sy2,rr,n in self.tracks:
            if n==net: continue
            d=seg_dist_to_point(x,y,sx1,sy1,sx2,sy2)
            if d - rr - r - clearance(net,n) < -0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            d=rect_point_dist(x,y,(px1,py1,px2,py2))
            if d - r - clearance(net,n) < -0.001: return False
        return True
    def add_track(self,x1,y1,x2,y2,w,net): self.tracks.append((x1,y1,x2,y2,w/2.0,net))
    def add_via(self,x,y,r,net): self.vias.append((x,y,r,net))

def add_track_obj(x1,y1,x2,y2,layer,w,net):
    t=pcbnew.PCB_TRACK(brd)
    t.SetStart(pcbnew.VECTOR2I(int(round(x1*MM)),int(round(y1*MM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(x2*MM)),int(round(y2*MM))))
    t.SetLayer(layer); t.SetWidth(int(round(w*MM))); t.SetNet(net); brd.Add(t)

def add_via_obj(x,y,vd,drill,net):
    v=pcbnew.PCB_VIA(brd)
    v.SetPosition(pcbnew.VECTOR2I(int(round(x*MM)),int(round(y*MM))))
    v.SetNet(net); v.SetWidth(int(round(vd*MM))); v.SetDrill(int(round(drill*MM)))
    v.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); v.SetRemoveUnconnected(False); brd.Add(v)

def add_routed(pts,layer,w,net,obs):
    if len(pts)<2: return False
    for i in range(len(pts)-1):
        x1,y1=pts[i]; x2,y2=pts[i+1]
        if math.hypot(x1-x2,y1-y2)<0.01: continue
        if not obs.track_clear(x1,y1,x2,y2,w,net.GetNetname()): return False
    for i in range(len(pts)-1):
        x1,y1=pts[i]; x2,y2=pts[i+1]
        if math.hypot(x1-x2,y1-y2)<0.01: continue
        add_track_obj(x1,y1,x2,y2,layer,w,net); obs.add_track(x1,y1,x2,y2,w,net.GetNetname())
    return True

pads_by_ref={}
for fp in brd.GetFootprints():
    for p in fp.Pads():
        pads_by_ref[(fp.GetReference(), str(p.GetNumber()))]=(fp,p,get_pad_rect(p))

def pad_info(it):
    m=re.match(r'(?:PTH )?Pad (\d+)', it['type'])
    if m and it['ref']:
        return pads_by_ref.get((it['ref'], m.group(1)))
    return None

def exact_track_nearest(track, px, py):
    sx=track.GetStart().x/MM; sy=track.GetStart().y/MM
    ex=track.GetEnd().x/MM; ey=track.GetEnd().y/MM
    dx=ex-sx; dy=ey-sy; l2=dx*dx+dy*dy
    if l2==0: return (sx, sy)
    t=max(0.0,min(1.0,((px-sx)*dx+(py-sy)*dy)/l2))
    return (sx+t*dx, sy+t*dy)

def track_endpoints_nm(t):
    return (t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)

def find_track_exact(drc_point, other_pt, net, layer_str):
    px,py=drc_point; ox,oy=other_pt
    best=None; bd=1e9; bestlen=-1
    for t in brd.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            if t.GetNetname()!=net: continue
            if 'F.Cu - B.Cu' not in layer_str: continue
            x=t.GetPosition().x/MM; y=t.GetPosition().y/MM
            d=math.hypot(x-px,y-py)
            if d < bd: bd=d; best=t
        elif isinstance(t, pcbnew.PCB_TRACK):
            if t.GetNetname()!=net: continue
            if layer_str=='F.Cu' and t.GetLayer()!=pcbnew.F_Cu: continue
            if layer_str=='B.Cu' and t.GetLayer()!=pcbnew.B_Cu: continue
            sx=t.GetStart().x/MM; sy=t.GetStart().y/MM; ex=t.GetEnd().x/MM; ey=t.GetEnd().y/MM
            nx,ny = exact_track_nearest(t, ox, oy)
            d_to_drc = math.hypot(nx-px, ny-py)
            length = math.hypot(ex-sx, ey-sy)
            if d_to_drc < 0.05 and length > 1e-6:
                score = d_to_drc - length*1e-6
                if score < bd:
                    bd=score; best=t; bestlen=length
    if isinstance(best, pcbnew.PCB_VIA):
        x=best.GetPosition().x/MM; y=best.GetPosition().y/MM
        return (x,y,False,None)
    if best:
        sx,sy,ex,ey = track_endpoints_nm(best)
        d_s = (sx-ox*MM)**2 + (sy-oy*MM)**2
        d_e = (ex-ox*MM)**2 + (ey-oy*MM)**2
        if d_s <= d_e:
            return (sx/MM, sy/MM, False, None)
        else:
            return (ex/MM, ey/MM, False, None)
    return (px,py,False,None)

def connection_point(it, other_pt):
    typ=it['type']; net=it['net']
    if 'Pad' in typ:
        info=pad_info(it)
        if info:
            p=info[1]
            x=p.GetPosition().x/MM; y=p.GetPosition().y/MM
            rect=get_pad_rect(p)
            return (x, y, True, rect)
    return find_track_exact((it['x'], it['y']), other_pt, net, it['layer_raw'])

def parse_pairs():
    text=open(DRC_PATH).read()
    blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
    pairs=[]
    for block in blocks[1:]:
        items=[]
        for line in block.split('\n'):
            m=re.match(r'\s+@\(([\-\d\.]+) mm, ([\-\d\.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) \[([^\]]+)\](?: of ([^\n]+?))?(?: on ([\w\. \-]+))?', line)
            if m:
                layer=m.group(6).strip() if m.group(6) else 'F.Cu - B.Cu'
                if 'PTH' in m.group(3): layer='F.Cu - B.Cu'
                items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer_raw':layer})
        if len(items)==2:
            pairs.append(items)
    return pairs

f_obs=ObstacleSet(brd, pcbnew.F_Cu)
b_obs=ObstacleSet(brd, pcbnew.B_Cu)
obs_map={pcbnew.F_Cu:f_obs, pcbnew.B_Cu:b_obs}

existing_vias=set()
for t in brd.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        existing_vias.add((round(t.GetPosition().x/MM,4), round(t.GetPosition().y/MM,4), t.GetNetname()))

def place_via(x,y,net):
    vd,drill=via_size(net.GetNetname()); r=vd/2.0
    k=(round(x,4), round(y,4), net.GetNetname())
    if k in existing_vias: return None
    if not f_obs.point_safe(x,y,r,net.GetNetname()) or not b_obs.point_safe(x,y,r,net.GetNetname()): return None
    add_via_obj(x,y,vd,drill,net)
    f_obs.add_via(x,y,r,net.GetNetname()); b_obs.add_via(x,y,r,net.GetNetname())
    existing_vias.add(k)
    return (x,y,vd,drill)

def safe_via_point(x,y,net, start_r=0.0):
    vd,drill=via_size(net.GetNetname()); r=vd/2.0
    if f_obs.point_safe(x,y,r,net.GetNetname()) and b_obs.point_safe(x,y,r,net.GetNetname()): return (x,y,vd,drill)
    radii=[0.15,0.25,0.35,0.5,0.75,1.0,1.25,1.5,2.0,2.5,3.0,3.5,4.0,5.0,6.0,7.0,8.0,9.0,10.0]
    for radius in radii:
        if start_r and radius<start_r: continue
        n=max(8,int(radius*20))
        for i in range(n):
            a=2*math.pi*i/n; px=x+radius*math.cos(a); py=y+radius*math.sin(a)
            if f_obs.point_safe(px,py,r,net.GetNetname()) and b_obs.point_safe(px,py,r,net.GetNetname()):
                return (px,py,vd,drill)
    return None

def short_track_to_via(start, via_pos, layer, width, net, obs):
    if math.hypot(start[0]-via_pos[0], start[1]-via_pos[1])<0.01: return True
    if obs.track_clear(start[0],start[1],via_pos[0],via_pos[1],width,net.GetNetname()):
        add_track_obj(start[0],start[1],via_pos[0],via_pos[1],layer,width,net); obs.add_track(start[0],start[1],via_pos[0],via_pos[1],width,net.GetNetname()); return True
    # L-shape
    for corner in [(start[0],via_pos[1]),(via_pos[0],start[1])]:
        if obs.track_clear(start[0],start[1],corner[0],corner[1],width,net.GetNetname()) and obs.track_clear(corner[0],corner[1],via_pos[0],via_pos[1],width,net.GetNetname()):
            add_track_obj(start[0],start[1],corner[0],corner[1],layer,width,net); obs.add_track(start[0],start[1],corner[0],corner[1],width,net.GetNetname())
            add_track_obj(corner[0],corner[1],via_pos[0],via_pos[1],layer,width,net); obs.add_track(corner[0],corner[1],via_pos[0],via_pos[1],width,net.GetNetname()); return True
    return False

def via_for_item(it, other_pt):
    net=brd.FindNet(it['net'])
    if not net: return None
    pt=connection_point(it, other_pt)
    if not pt: return None
    x,y,is_pad,rect=pt
    # try inside pad first
    if is_pad and rect:
        for dx in [0,0.05,-0.05,0.1,-0.1,0.15,-0.15,0.2,-0.2,0.25,-0.25,0.3,-0.3]:
            for dy in [0,0.05,-0.05,0.1,-0.1,0.15,-0.15,0.2,-0.2,0.25,-0.25,0.3,-0.3]:
                px,py=x+dx,y+dy
                if not point_in_pad(px,py,rect,0.05): continue
                v=place_via(px,py,net)
                if v: return v
    v=safe_via_point(x,y,net)
    if not v: return None
    placed=place_via(v[0],v[1],net)
    if not placed: return None
    # short track from item to via if outside pad
    if is_pad and rect and not point_in_pad(v[0],v[1],rect,0.0):
        layer=pcbnew.F_Cu if 'F.Cu' in it['layer_raw'] else pcbnew.B_Cu
        width=track_width(net.GetNetname())
        obs=obs_map[layer]
        if not short_track_to_via((x,y), (v[0],v[1]), layer, width, net, obs):
            return None
    elif not is_pad and ('F.Cu' in it['layer_raw'] or 'B.Cu' in it['layer_raw']):
        layer=pcbnew.F_Cu if 'F.Cu' in it['layer_raw'] else pcbnew.B_Cu
        width=track_width(net.GetNetname())
        obs=obs_map[layer]
        short_track_to_via((x,y), (v[0],v[1]), layer, width, net, obs)
    return v

def layers(it):
    s=it['layer_raw']
    return {'F':'F.Cu' in s, 'B':'B.Cu' in s}

def corners(x1,y1,x2,y2, span=5.0, step=0.25):
    offs=[0]; o=step
    while o<=span:
        offs.extend([o,-o]); o+=step
    midx=(x1+x2)/2.0; midy=(y1+y2)/2.0
    cand=set()
    for ox in offs:
        for oy in offs:
            cand.add((x1+ox,y2+oy)); cand.add((x2+ox,y1+oy))
            cand.add((midx+ox,y1+oy)); cand.add((midx+ox,y2+oy))
            cand.add((x1+ox,midy+oy)); cand.add((x2+ox,midy+oy))
            cand.add((midx+ox,midy+oy))
    # add board edge corridor points
    cand.add((BOARD_LEFT+EDGE_MARGIN+0.3, y1)); cand.add((BOARD_LEFT+EDGE_MARGIN+0.3, y2))
    cand.add((BOARD_RIGHT-EDGE_MARGIN-0.3, y1)); cand.add((BOARD_RIGHT-EDGE_MARGIN-0.3, y2))
    cand.add((x1, BOARD_BOTTOM+EDGE_MARGIN+0.3)); cand.add((x2, BOARD_BOTTOM+EDGE_MARGIN+0.3))
    cand.add((x1, BOARD_TOP-EDGE_MARGIN-0.3)); cand.add((x2, BOARD_TOP-EDGE_MARGIN-0.3))
    return list(cand)

def board_waypoints(p1,p2):
    # a few perimeter waypoints useful for long paths
    w=[]
    for y in [BOARD_BOTTOM+EDGE_MARGIN+0.5, BOARD_TOP-EDGE_MARGIN-0.5]:
        for x in [BOARD_LEFT+EDGE_MARGIN+0.5, (p1[0]+p2[0])/2.0, BOARD_RIGHT-EDGE_MARGIN-0.5]:
            w.append((x,y))
    for x in [BOARD_LEFT+EDGE_MARGIN+0.5, BOARD_RIGHT-EDGE_MARGIN-0.5]:
        for y in [BOARD_BOTTOM+EDGE_MARGIN+0.5, (p1[1]+p2[1])/2.0, BOARD_TOP-EDGE_MARGIN-0.5]:
            w.append((x,y))
    return w

def try_layer(p1,p2,layer,net,width):
    obs=obs_map[layer]
    if add_routed([p1,p2], layer, width, net, obs): return True
    for cx,cy in corners(p1[0],p1[1],p2[0],p2[1]):
        if add_routed([p1,(cx,cy),p2], layer, width, net, obs): return True
    return False

def try_via_bridge(p1,p2,net, p1_is_f, p2_is_f):
    width=track_width(net.GetNetname())
    v1=safe_via_point(p1[0],p1[1],net)
    v2=safe_via_point(p2[0],p2[1],net)
    if not v1 or not v2: return False
    layer1=pcbnew.F_Cu if p1_is_f else pcbnew.B_Cu
    layer2=pcbnew.F_Cu if p2_is_f else pcbnew.B_Cu
    # route from p1 to v1, p2 to v2
    if not short_track_to_via(p1, (v1[0],v1[1]), layer1, width, net, obs_map[layer1]): return False
    if not short_track_to_via(p2, (v2[0],v2[1]), layer2, width, net, obs_map[layer2]): return False
    placed1=place_via(v1[0],v1[1],net); placed2=place_via(v2[0],v2[1],net)
    if not placed1 or not placed2:
        return False
    # connect vias on B.Cu with straight or L or perimeter waypoints
    if b_obs.track_clear(v1[0],v1[1],v2[0],v2[1],width,net.GetNetname()):
        add_track_obj(v1[0],v1[1],v2[0],v2[1],pcbnew.B_Cu,width,net); b_obs.add_track(v1[0],v1[1],v2[0],v2[1],width,net.GetNetname()); return True
    for cx,cy in corners(v1[0],v1[1],v2[0],v2[1], span=10.0, step=0.5):
        if add_routed([(v1[0],v1[1]),(cx,cy),(v2[0],v2[1])], pcbnew.B_Cu, width, net, b_obs): return True
    # try 2-segment (3 segments) with board waypoints
    for w1 in board_waypoints((v1[0],v1[1]),(v2[0],v2[1])):
        for w2 in board_waypoints((v1[0],v1[1]),(v2[0],v2[1])):
            if add_routed([(v1[0],v1[1]),w1,w2,(v2[0],v2[1])], pcbnew.B_Cu, width, net, b_obs): return True
    return False

def handle_plane_pair(it1,it2):
    net=brd.FindNet(it1['net'])
    if not net: return False
    # place via for each endpoint; plane connects them
    p2_init=(it2['x'],it2['y'])
    v1=via_for_item(it1, p2_init)
    v2=via_for_item(it2, (it1['x'],it1['y']))
    return bool(v1) or bool(v2)

def handle_signal_pair(it1,it2):
    if it1['net']!=it2['net']: return False
    net=brd.FindNet(it1['net'])
    if not net: return False
    p2_init=(it2['x'],it2['y'])
    p1=connection_point(it1, p2_init)
    p2=connection_point(it2, (p1[0],p1[1]))
    p1=connection_point(it1, (p2[0],p2[1]))
    width=track_width(net.GetNetname())
    l1=layers(it1); l2=layers(it2)
    common=[]
    if l1['F'] and l2['F']: common.append(pcbnew.F_Cu)
    if l1['B'] and l2['B']: common.append(pcbnew.B_Cu)
    for layer in common:
        if try_layer((p1[0],p1[1]),(p2[0],p2[1]),layer,net,width): return True
    if try_via_bridge((p1[0],p1[1]),(p2[0],p2[1]),net, l1['F'], l2['F']): return True
    return False

pairs=parse_pairs()
print('pairs', len(pairs))

plane_added=plane_skipped=signal_added=signal_skipped=zone_skip=0
for p in pairs:
    it1,it2=p
    if it1['type']=='Zone' or it2['type']=='Zone':
        zone_skip+=1; continue
    if it1['net'] in PLANE_NETS:
        if handle_plane_pair(it1,it2): plane_added+=1
        else: plane_skipped+=1
    else:
        if handle_signal_pair(it1,it2): signal_added+=1
        else: signal_skipped+=1

print('plane_added',plane_added,'plane_skipped',plane_skipped,'signal_added',signal_added,'signal_skipped',signal_skipped,'zone_skip',zone_skip)

for z in brd.Zones():
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
filler=pcbnew.ZONE_FILLER(brd); filler.Fill(brd.Zones())
brd.BuildConnectivity()
pcbnew.SaveBoard(BOARD_PATH, brd)
print('saved')
