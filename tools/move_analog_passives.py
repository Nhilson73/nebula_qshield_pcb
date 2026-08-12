import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
moves={
    'C20': (0, 2.0),
    'C21': (0, 2.0),
    'C23': (0, 2.0),
    'R30': (0, 2.0),
    'R31': (0, 2.0),
    'R32': (0, 2.0),
}
for ref,(dx,dy) in moves.items():
    fp=b.FindFootprintByReference(ref)
    if not fp: print(ref,'not found'); continue
    p=fp.GetPosition(); oldx=p.x/MM; oldy=p.y/MM
    fp.SetPosition(pcbnew.VECTOR2I(int((oldx+dx)*MM), int((oldy+dy)*MM)))
    print(ref, 'moved from', oldx, oldy, 'to', oldx+dx, oldy+dy)
# clear selection etc.
b.BuildConnectivity()
pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
print('saved')
