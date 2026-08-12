import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
for d in b.GetDrawings():
    if d.GetLayer()==pcbnew.Edge_Cuts and hasattr(d,'GetStart'):
        s=d.GetStart(); e=d.GetEnd()
        x1,y1=s.x/1e6, s.y/1e6
        x2,y2=e.x/1e6, e.y/1e6
        if (40<=x1<=100 and 80<=y1<=100) or (40<=x2<=100 and 80<=y2<=100):
            print(x1,y1,'->',x2,y2)
