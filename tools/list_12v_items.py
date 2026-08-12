import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
items=[]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname()=='/12V_RAIL':
            items.append(('pad', fp.GetReference(), p.GetNumber(), p.GetPosition().x/MM, p.GetPosition().y/MM))
for t in b.GetTracks():
    if t.GetNetname()=='/12V_RAIL':
        if isinstance(t, pcbnew.PCB_VIA):
            items.append(('via', '', '', t.GetPosition().x/MM, t.GetPosition().y/MM))
        elif isinstance(t, pcbnew.PCB_TRACK):
            items.append(('track','','', t.GetStart().x/MM, t.GetStart().y/MM, t.GetEnd().x/MM, t.GetEnd().y/MM))
for it in sorted(items, key=lambda x: (x[3], x[4] if len(x)>4 else 0)):
    print(it)
