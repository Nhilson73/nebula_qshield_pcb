import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
conn=b.GetConnectivity()
conn.Build(b)
# use FillIsolatedIslandsMap? It requires a map argument. Try simpler: get connected items for each /12V_RAIL item
items=[]
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname()=='/12V_RAIL':
            items.append(('pad', fp.GetReference()+'.'+p.GetNumber(), p, p.GetPosition().x/MM, p.GetPosition().y/MM))
for t in b.GetTracks():
    if t.GetNetname()=='/12V_RAIL':
        if isinstance(t, pcbnew.PCB_VIA):
            items.append(('via', '', t, t.GetPosition().x/MM, t.GetPosition().y/MM))
        elif isinstance(t, pcbnew.PCB_TRACK):
            items.append(('track','',t,(t.GetStart().x/MM+t.GetEnd().x/MM)/2,(t.GetStart().y/MM+t.GetEnd().y/MM)/2))
# group by connectivity: use GetNetItems? 
for it in items[:15]:
    obj=it[2]
    if isinstance(obj, (pcbnew.PAD, pcbnew.PCB_VIA, pcbnew.PCB_TRACK)):
        connected=conn.GetConnectedItems(obj)
        print(it[0], it[1], it[3], it[4], 'connected count', len(connected))
