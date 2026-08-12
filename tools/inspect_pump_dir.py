import pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
for t in b.GetTracks():
    if isinstance(t, pcbnew.PCB_TRACK) and t.GetNetname()=='/PUMP_DIR':
        s=t.GetStart(); e=t.GetEnd()
        print(t.GetWidth()/1e6, s.x/1e6,s.y/1e6, e.x/1e6,e.y/1e6, t.GetLength()/1e6)
