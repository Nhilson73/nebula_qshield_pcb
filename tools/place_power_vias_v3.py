#!/usr/bin/env python3
import re, math, pcbnew
MM = 1_000_000
BOARD_PATH = '/workspace/kicad/nebula_qshield.kicad_pcb'
DRC_PATH = '/workspace/kicad/nebula_qshield-drc.rpt'
VIA_D = 0.6
DRILL = 0.3
VR = VIA_D / 2.0

brd = pcbnew.LoadBoard(BOARD_PATH)
def get_pad_rect(p):
    bb = p.GetBoundingBox(); return (bb.GetX()/MM, bb.GetY()/MM, (bb.GetX()+bb.GetWidth())/MM, (bb.GetY()+bb.GetHeight())/MM)
def rect_dist(px, py, r):
    x1,y1,x2,y2=r; dx=max(max(x1-px,0.0),px-x2); dy=max(max(y1-py,0.0),py-y2); return math.hypot(dx,dy)
def seg_dist(px, py, x1, y1, x2, y2):
    dx=x2-x1; dy=y2-y1; l2=dx*dx+dy*dy
    if l2==0: return math.hypot(px-x1,py-y1)
    t=max(0.0,min(1.0,((px-x1)*dx+(py-y1)*dy)/l2)); cx=x1+t*dx; cy=y1+t*dy; return math.hypot(px-cx,py-cy)

def netclass_clearance(netname, other_net):
    if 'Analog' in netname or 'Analog' in other_net or '_SIG' in netname or '_ADC' in netname or '_FILT' in netname or '_ATT' in netname: return 0.35
    if any(s in netname or s in other_net for s in ['/12V','/5V','/3V3','VIN_12V','12V_FUSED','CHILLER','MOTOR','COIL','/Actuator']): return 0.30
    if 'I2C' in netname or 'I2C' in other_net: return 0.25
    return 0.25

class ObstacleSet:
    def __init__(self, brd, layer_id):
        self.vias=[]; self.tracks=[]; self.pads=[]; self.layer=layer_id
        for t in brd.GetTracks():
            if isinstance(t, pcbnew.PCB_VIA):
                if not t.GetLayerSet().Contains(layer_id): continue
                r=t.GetWidth(layer_id)/2.0/MM; pos=t.GetPosition(); self.vias.append((pos.x/MM,pos.y/MM,r,t.GetNetname()))
            elif isinstance(t, pcbnew.PCB_TRACK):
                if t.GetLayer()!=layer_id: continue
                r=t.GetWidth()/2.0/MM; s=t.GetStart(); e=t.GetEnd(); self.tracks.append((s.x/MM,s.y/MM,e.x/MM,e.y/MM,r,t.GetNetname()))
        for fp in brd.GetFootprints():
            for p in fp.Pads():
                if not p.GetLayerSet().Contains(layer_id): continue
                rect=get_pad_rect(p); self.pads.append((rect[0],rect[1],rect[2],rect[3],p.GetNetname()))
    def point_safe(self, x, y, radius, net):
        for vx,vy,r,n in self.vias:
            if n==net: continue
            if math.hypot(x-vx,y-vy)-r-radius-netclass_clearance(net,n)<-0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            if seg_dist(x,y,sx1,sy1,sx2,sy2)-r-radius-netclass_clearance(net,n)<-0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            d=rect_dist(x,y,(px1,py1,px2,py2))
            if d-radius-netclass_clearance(net,n)<-0.001: return False
        return True
    def track_clear(self, x1,y1,x2,y2,width,net):
        hw=width/2.0
        for vx,vy,r,n in self.vias:
            if n==net: continue
            if seg_dist(vx,vy,x1,y1,x2,y2)-r-hw-netclass_clearance(net,n)<-0.001: return False
        for sx1,sy1,sx2,sy2,r,n in self.tracks:
            if n==net: continue
            dx=seg_dist(x1,y1,sx1,sy1,sx2,sy2)-r-hw-netclass_clearance(net,n); dy=seg_dist(x2,y2,sx1,sy1,sx2,sy2)-r-hw-netclass_clearance(net,n)
            if seg_dist(0,0,x1,y1,x2,y2)<1e-9: continue
            t=max(0.0,min(1.0,((sx1-x1)*(x2-x1)+(sy1-y1)*(y2-y1))/((x2-x1)**2+(y2-y1)**2)))
            for ti in [0,0.5,1]:
                px=x1+t*(x2-x1); py=y1+t*(y2-y1)
                d=seg_dist(px,py,sx1,sy1,sx2,sy2)-r-hw-netclass_clearance(net,n)
                if d<-0.001: return False
        for px1,py1,px2,py2,n in self.pads:
            if n==net: continue
            # check segment against rect edges
            min_d=min(seg_dist(x1,y1,px1,py1,px2,py1),seg_dist(x1,y1,px2,py1,px2,py2),seg_dist(x1,y1,px2,py2,px1,py2),seg_dist(x1,y1,px1,py2,px1,py1),seg_dist(x2,y2,px1,py1,px2,py1),seg_dist(x2,y2,px2,py1,px2,py2),seg_dist(x2,y2,px2,py2,px1,py2),seg_dist(x2,y2,px1,py2,px1,py1))
            if min_d - hw - netclass_clearance(net,n) < -0.001: return False
        return True
    def add_via(self, x,y,r,net): self.vias.append((x,y,r,net))
    def add_track(self, x1,y1,x2,y2,w,net): self.tracks.append((x1,y1,x2,y2,w/2.0,net))

f_obs = ObstacleSet(brd, pcbnew.F_Cu)
b_obs = ObstacleSet(brd, pcbnew.B_Cu)

text = open(DRC_PATH).read()
blocks = re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    for line in block.split('\n'):
        m = re.match(r'\s+@\(([\-\d\.]+) mm, ([\-\d\.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) \[([^\]]+)\](?: of ([^ ]+))?(?: on ([\w\. \-]+))?', line)
        if m:
            layer=m.group(6).strip() if m.group(6) else ('F.Cu - B.Cu' if 'PTH' in m.group(3) else 'F.Cu')
            if 'PTH' in m.group(3): layer='F.Cu - B.Cu'
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer_raw':layer})
    if len(items)==2:
        pairs.append(items)

power_nets = {'/12V_RAIL','/5V_RAIL','/3V3_RAIL'}
pairs = [p for p in pairs if p[0]['net'] in power_nets]
print('power pairs', len(pairs))

pad_by_ref={}
for fp in brd.GetFootprints():
    for p in fp.Pads():
        pad_by_ref[(fp.GetReference(), str(p.GetNumber()))] = (fp, p, get_pad_rect(p))

def pad_of(it):
    m=re.match(r'(?:PTH )?Pad (\d+)', it['type'])
    if m and it['ref']:
        return pad_by_ref.get((it['ref'], m.group(1)))
    return None

existing_vias = set()
for t in brd.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        existing_vias.add((round(t.GetPosition().x/MM,3), round(t.GetPosition().y/MM,3), t.GetNetname()))

def add_via(x, y, net):
    k=(round(x,3), round(y,3), net.GetNetname())
    if k in existing_vias: return False
    if not f_obs.point_safe(x,y,VR,net.GetNetname()) or not b_obs.point_safe(x,y,VR,net.GetNetname()): return False
    via = pcbnew.PCB_VIA(brd)
    via.SetPosition(pcbnew.VECTOR2I(int(round(x*MM)), int(round(y*MM))))
    via.SetNet(net); via.SetWidth(int(round(VIA_D*MM))); via.SetDrill(int(round(DRILL*MM)))
    via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); via.SetRemoveUnconnected(False); brd.Add(via)
    f_obs.add_via(x,y,VR,net.GetNetname()); b_obs.add_via(x,y,VR,net.GetNetname())
    existing_vias.add(k)
    return True

def add_track(x1,y1,x2,y2, layer_id, width, net, obs):
    if math.hypot(x1-x2,y1-y2)<0.01: return False
    if obs.track_clear(x1,y1,x2,y2,width,net.GetNetname()):
        t=pcbnew.PCB_TRACK(brd)
        t.SetStart(pcbnew.VECTOR2I(int(round(x1*MM)),int(round(y1*MM))))
        t.SetEnd(pcbnew.VECTOR2I(int(round(x2*MM)),int(round(y2*MM))))
        t.SetLayer(layer_id); t.SetWidth(int(round(width*MM))); t.SetNet(net); brd.Add(t)
        obs.add_track(x1,y1,x2,y2,width,net.GetNetname())
        return True
    return False

def place_via_in_pad(it, net):
    info=pad_of(it)
    if not info: return None
    fp,p,rect=info; cx=(rect[0]+rect[2])/2.0; cy=(rect[1]+rect[3])/2.0
    for dx in [0,0.05,-0.05,0.1,-0.1,0.15,-0.15,0.2,-0.2,0.25,-0.25,0.3,-0.3]:
        for dy in [0,0.05,-0.05,0.1,-0.1,0.15,-0.15,0.2,-0.2,0.25,-0.25,0.3,-0.3]:
            px,py=cx+dx,cy+dy
            if not (rect[0]+VR<=px<=rect[2]-VR and rect[1]+VR<=py<=rect[3]-VR): continue
            if f_obs.point_safe(px,py,VR,net.GetNetname()) and b_obs.point_safe(px,py,VR,net.GetNetname()):
                return (px,py)
    return None

def place_via_near_point(x, y, net, max_r=8.0):
    radii=[0,0.25,0.5,0.75,1.0,1.25,1.5,2.0,2.5,3.0,3.5,4.0,5.0,6.0,7.0,8.0]
    for r in radii:
        if r>max_r: break
        n=max(8,int(r*24))
        for i in range(n):
            a=2*math.pi*i/n; px=x+r*math.cos(a); py=y+r*math.sin(a)
            if f_obs.point_safe(px,py,VR,net.GetNetname()) and b_obs.point_safe(px,py,VR,net.GetNetname()):
                return (px,py)
    return None

def short_track_to_via(x, y, vx, vy, layer_id, width, net, obs, attempts=4):
    if math.hypot(x-vx,y-vy)<0.01: return True
    if add_track(x,y,vx,vy,layer_id,width,net,obs): return True
    # L-shape corners
    for mx in [x, vx, (x+vx)/2.0, x+0.5*(vx-x), x-0.5, x+0.5]:
        for my in [y, vy, (y+vy)/2.0, y+0.5*(vy-y), y-0.5, y+0.5]:
            if add_track(x,y,mx,my,layer_id,width,net,obs) and add_track(mx,my,vx,vy,layer_id,width,net,obs):
                return True
    return False

added_vias=0; added_tracks=0; skipped=0
for it1, it2 in pairs:
    net = brd.FindNet(it1['net'])
    if not net: skipped+=1; continue
    vias=[]
    for it in [it1,it2]:
        pos=None; layer=pcbnew.F_Cu
        info=pad_of(it)
        if info:
            fp,p,rect=info; cx=(rect[0]+rect[2])/2.0; cy=(rect[1]+rect[3])/2.0
            # pad layer
            if 'B.Cu' in it['layer_raw'] and 'F.Cu' not in it['layer_raw']: layer=pcbnew.B_Cu
            else: layer=pcbnew.F_Cu
            pos=place_via_in_pad(it, net)
        if pos:
            if add_via(pos[0],pos[1],net): added_vias+=1; vias.append(pos); continue
        # find nearest safe point for via
        pos=place_via_near_point(it['x'], it['y'], net)
        if pos:
            # short track from pad or track to via
            if info:
                start=(cx,cy)
            else:
                start=(it['x'],it['y'])
            obs=f_obs if layer==pcbnew.F_Cu else b_obs
            if short_track_to_via(start[0],start[1],pos[0],pos[1],layer,0.5,net,obs):
                added_tracks+=1
            if add_via(pos[0],pos[1],net):
                added_vias+=1; vias.append(pos)
            else:
                vias.append(None)
        else:
            vias.append(None)
    # For power nets rely on the internal plane (In2.Cu) to connect the vias;
    # do not add outer-layer bridging tracks unless the plane is split (handled below).
    # if vias[0] and vias[1]:
    #    for layer_id, obs in [(pcbnew.B_Cu, b_obs), (pcbnew.F_Cu, f_obs)]:
    #        if add_track(vias[0][0],vias[0][1],vias[1][0],vias[1][1],layer_id,0.5,net,obs):
    #            added_tracks+=1; break

for z in brd.Zones(): z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
filler=pcbnew.ZONE_FILLER(brd); filler.Fill(brd.Zones())
brd.BuildConnectivity()
pcbnew.SaveBoard(BOARD_PATH, brd)
print(f'added vias {added_vias}, tracks {added_tracks}, skipped {skipped}')
