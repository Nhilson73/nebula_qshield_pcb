import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1_000_000
net=b.FindNet('/PUMP_DIR')
def near(a,b,tol=0.01):
    return abs(a[0]-b[0])<tol and abs(a[1]-b[1])<tol

# remove the segment that violates edge clearance
removed=0
for t in list(b.GetTracks()):
    if isinstance(t, pcbnew.PCB_TRACK) and t.GetNetname()=='/PUMP_DIR':
        s=(t.GetStart().x/MM, t.GetStart().y/MM)
        e=(t.GetEnd().x/MM, t.GetEnd().y/MM)
        if (near(s,(58.2681,89.3054)) and near(e,(79.1525,88.1987))) or (near(e,(58.2681,89.3054)) and near(s,(79.1525,88.1987))):
            print('remove', s, e)
            b.Remove(t); removed+=1

# add replacement L under cutout
width=0.25*MM
def add(x1,y1,x2,y2):
    t=pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(int(round(x1*MM)),int(round(y1*MM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(x2*MM)),int(round(y2*MM))))
    t.SetLayer(pcbnew.F_Cu)
    t.SetWidth(int(round(0.25*MM)))
    t.SetNet(net)
    b.Add(t)

add(58.2681,89.3054, 58.2681,88.15)
add(58.2681,88.15, 79.1525,88.15)
add(79.1525,88.15, 79.1525,88.1987)
print('added replacement')
pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
