import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6

# find K1/K2 pads positions
pads={}
for fp in b.GetFootprints():
    ref=fp.GetReference()
    if ref in ['K1','K2']:
        pads[ref]={}
        for p in fp.Pads():
            pads[ref][str(p.GetNumber())]=(p.GetPosition().x/MM, p.GetPosition().y/MM, p)

tracks=list(b.GetTracks())
for ref in ['K1','K2']:
    if ref not in pads or '5' not in pads[ref] or '6' not in pads[ref]: continue
    p5=pads[ref]['5']; p6=pads[ref]['6']
    print(ref,'p5',p5[:2],'p6',p6[:2])
    for t in tracks:
        if isinstance(t, pcbnew.PCB_TRACK):
            sx=t.GetStart().x/MM; sy=t.GetStart().y/MM; ex=t.GetEnd().x/MM; ey=t.GetEnd().y/MM
            matches_p5=(abs(sx-p5[0])<0.01 and abs(sy-p5[1])<0.01) or (abs(ex-p5[0])<0.01 and abs(ey-p5[1])<0.01)
            matches_p6=(abs(sx-p6[0])<0.01 and abs(sy-p6[1])<0.01) or (abs(ex-p6[0])<0.01 and abs(ey-p6[1])<0.01)
            if matches_p5 and matches_p6:
                print(' remove track', t.GetNetname(), sx,sy,ex,ey)
                b.Remove(t)
    for num in ['5','6']:
        p=pads[ref][num][2]
        p.SetNetCode(0)
        print(ref, 'pad', num, '-> no-connect')
b.BuildConnectivity()
pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
print('saved')
