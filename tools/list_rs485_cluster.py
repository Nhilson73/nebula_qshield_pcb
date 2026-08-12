import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
refs=['U22','U23','Y1','C31','C32','C33','R38','U15']
for ref in refs:
    fp=b.FindFootprintByReference(ref)
    if not fp: print(ref,'not found'); continue
    print(ref, fp.GetPosition().x/MM, fp.GetPosition().y/MM, fp.GetValue())
