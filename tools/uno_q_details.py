import pcbnew, math
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
fp=b.FindFootprintByReference('J21')
ox=fp.GetPosition().x/MM; oy=fp.GetPosition().y/MM
print('J21 origin (UNO Q lower-left)', ox, oy)
# UNO Q board outline: 68.58 x 53.34, corner radius 1.6
print('UNO Q board envelope: x', ox, ox+68.58, 'y', oy, oy+53.34)
# list J21 pads/holes positions and sizes
pads=[]; holes=[]
for p in fp.Pads():
    x=p.GetPosition().x/MM; y=p.GetPosition().y/MM
    size=(p.GetSize().x/MM, p.GetSize().y/MM)
    name=p.GetNumber()
    print('pad/hole', name, p.GetNetname(), x, y, 'size', size, 'posrel', x-ox, y-oy)
    pads.append((x,y,size))
