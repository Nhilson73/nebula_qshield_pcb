import sys
import pcbnew

board_path = sys.argv[1] if len(sys.argv) > 1 else '/workspace/kicad/nebula_qshield.kicad_pcb'
dsn_path = sys.argv[2] if len(sys.argv) > 2 else '/workspace/kicad/nebula_qshield.dsn'

board = pcbnew.LoadBoard(board_path)
print('loaded', board.GetFileName())
print('nets', len(list(board.GetNetInfo().NetsByName())))
print('tracks', len(board.GetTracks()))
print('vias', len([t for t in board.GetTracks() if isinstance(t, pcbnew.PCB_VIA)]))
print('zones', len(board.Zones()))
board.ExportSpecctraDSN(dsn_path)
print('dsn exported to', dsn_path)
