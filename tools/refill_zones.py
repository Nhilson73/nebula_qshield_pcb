import pcbnew

BOARD = '/workspace/kicad/nebula_qshield_100x120.kicad_pcb'
board = pcbnew.LoadBoard(BOARD)
print('loaded', len(list(board.GetFootprints())), 'footprints')
filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
board.BuildConnectivity()
board.Save(BOARD)
print('refilled zones and saved')
