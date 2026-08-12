import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
gnd_net=b.FindNet('GND')
removed=0
for t in list(b.GetTracks()):
    if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname()==gnd_net.GetNetname():
        x=t.GetPosition().x/1e6
        y=t.GetPosition().y/1e6
        if abs(x-87.465)<0.01 and abs(y-14.625)<0.01:
            b.Remove(t)
            removed+=1
print('removed', removed)
pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
