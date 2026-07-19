import pcbnew, json, os, sys

BOARD = '/workspace/kicad/nebula_qshield_100x120.kicad_pcb'
JSON = '/workspace/kicad/repack_positions.json'

with open(JSON) as f:
    placements = json.load(f)

board = pcbnew.LoadBoard(BOARD)
print('loaded', len(list(board.GetFootprints())), 'footprints', file=sys.stderr)

fps = {str(fp.GetReference()): fp for fp in list(board.GetFootprints())}

for ref, spec in placements.items():
    if ref not in fps:
        print(f'WARNING: {ref} not found', file=sys.stderr)
        continue
    fp = fps[ref]
    pos = pcbnew.VECTOR2I(int(spec['x'] * 1e6), int(spec['y'] * 1e6))
    fp.SetPosition(pos)
    fp.SetOrientationDegrees(spec['angle'])
    print(f'Moved {ref} to ({spec["x"]}, {spec["y"]}) angle {spec["angle"]}', file=sys.stderr)

board.Save(BOARD)
print('Saved', BOARD, file=sys.stderr)
