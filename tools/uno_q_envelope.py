import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
# J21 footprint position and pads
fp=b.FindFootprintByReference('J21')
print('J21 pos', fp.GetPosition().x/MM, fp.GetPosition().y/MM)
# Determine UNO Q board envelope: the doc coords are relative to UNO Q lower-left; J21 origin may be lower-left of footprint? Let's get bbox of all J21 pads/holes
bb=fp.GetBoundingBox()
print('J21 bbox', bb.GetX()/MM, bb.GetY()/MM, (bb.GetX()+bb.GetWidth())/MM, (bb.GetY()+bb.GetHeight())/MM)
# UNO Q board size 68.58 x 53.34. If lower-left is J21 position, envelope is x..x+68.58, y..y+53.34
ox=fp.GetPosition().x/MM; oy=fp.GetPosition().y/MM
print('envelope guess', ox, oy, ox+68.58, oy+53.34)
# Components inside envelope
in_env=[]
for f in b.GetFootprints():
    if f.GetReference()=='J21': continue
    p=f.GetPosition(); x=p.x/MM; y=p.y/MM
    if ox<=x<=ox+68.58 and oy<=y<=oy+53.34:
        in_env.append((f.GetReference(), x, y, f.GetValue()))
print('components inside envelope:', len(in_env))
for r,x,y,v in sorted(in_env):
    print(r,x,y,v)
