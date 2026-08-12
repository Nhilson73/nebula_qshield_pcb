import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
conn=b.GetConnectivity(); conn.Build(b)
MM=1e6
removed=0
for t in list(b.GetTracks()):
    if isinstance(t, pcbnew.PCB_VIA):
        # via is isolated if it has <=1 connected items (itself)
        if len(conn.GetConnectedItems(t))<=1:
            print('remove isolated via', t.GetNetname(), t.GetPosition().x/MM, t.GetPosition().y/MM)
            b.Remove(t); removed+=1
zones=b.Zones()
if zones:
    for z in zones:
        try:
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        except Exception as e:
            print('zone skip', e)
            pass
f=pcbnew.ZONE_FILLER(b); f.Fill(b.Zones())
b.BuildConnectivity()
pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
print('removed isolated vias', removed)
