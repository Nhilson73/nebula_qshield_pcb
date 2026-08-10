import pcbnew
import sys

board_path = sys.argv[1] if len(sys.argv) > 1 else '/workspace/kicad/nebula_qshield.kicad_pcb'

board = pcbnew.LoadBoard(board_path)
print('Loaded', board_path)

# Fill all zones
filler = pcbnew.ZONE_FILLER(board)
zones = board.Zones()
print('Filling', len(zones), 'zones')
filler.Fill(zones)
print('Done filling')

board.Save(board_path)
print('Saved', board_path)
