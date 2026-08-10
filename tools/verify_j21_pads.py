import pcbnew
board = pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
fp = board.FindFootprintByReference('J21')
fpx, fpy = fp.GetPosition()
for p in fp.Pads():
    x, y = p.GetPosition()
    local = (round((x - fpx) / 1e6, 2), round((y - fpy) / 1e6, 2))
    print(f"num={p.GetNumber()!s:<3} local=({local[0]:>6.2f}, {local[1]:>6.2f}) net={p.GetNetname()!s}")
