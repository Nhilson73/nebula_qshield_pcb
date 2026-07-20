import pcbnew, json, math, sys

BOARD = '/workspace/kicad/nebula_qshield.kicad_pcb'
OUT = '/workspace/kicad/repack_positions.json'

board = pcbnew.LoadBoard(BOARD)
print('loaded', len(list(board.GetFootprints())), 'footprints', file=sys.stderr)

def cy_bbox(fp):
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy.OutlineCount() == 0:
        cy = fp.GetCourtyard(pcbnew.B_CrtYd)
    if cy.OutlineCount() == 0:
        bb = fp.GetBoundingBox()
    else:
        bb = cy.BBox()
    return (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())

def local_cy(fp):
    old = fp.GetOrientationDegrees()
    fp.SetOrientationDegrees(0)
    bb = cy_bbox(fp)
    fp.SetOrientationDegrees(old)
    cx, cy = fp.GetPosition().x, fp.GetPosition().y
    return (bb[0]-cx, bb[1]-cy, bb[2]-cx, bb[3]-cy)

def bbox_at(local, pos, angle):
    rad = math.radians(angle)
    c = math.cos(rad); s = math.sin(rad)
    xs=[]; ys=[]
    for lx, ly in ((local[0],local[1]), (local[2],local[1]), (local[2],local[3]), (local[0],local[3])):
        x = c*lx - s*ly + pos.x
        y = s*lx + c*ly + pos.y
        xs.append(x); ys.append(y)
    return (min(xs), min(ys), max(xs), max(ys))

def overlaps(a, b, margin=0):
    return not (a[2] + margin < b[0] or a[0] - margin > b[2] or
                a[3] + margin < b[1] or a[1] - margin > b[3])

fps = {str(fp.GetReference()): fp for fp in list(board.GetFootprints())}
j21 = fps['J21']
j21_cy = cy_bbox(j21)

# movable set: overlaps J21 courtyard, plus known relocated problem children
movable = set()
for ref, fp in fps.items():
    if ref == 'J21':
        continue
    if overlaps(cy_bbox(fp), j21_cy, margin=0):
        movable.add(ref)
for ref in ('D10', 'U17', 'R36', 'R37'):
    if ref in fps:
        movable.add(ref)

print('initial movable:', sorted(movable), file=sys.stderr)

# Keep the relocation set small: only the components that intrude into the UNO Q
# courtyard or are known to be in the wrong place.  Fixed obstacles will naturally
# force these into the free top strip.
print('final movable:', sorted(movable), file=sys.stderr)

# fixed obstacles: J21, non-movable footprints, connector cutouts
obstacles = [j21_cy]
# Pin the I2C pull-ups next to the J21 D20/D21 pins (above the power-jack cutout)
forced_positions = {
    # 3.21 mm center spacing satisfies the 2.96 mm courtyard + 0.25 mm rule
    'R36': {'x': 65.67, 'y': 96.0, 'angle': 0},
    'R37': {'x': 68.88, 'y': 96.0, 'angle': 0},
}

movable_items = []
for ref, fp in fps.items():
    if ref == 'J21':
        continue
    bb = cy_bbox(fp)
    local = local_cy(fp)
    if ref in movable:
        if ref in forced_positions:
            continue
        area = (bb[2]-bb[0]) * (bb[3]-bb[1])
        movable_items.append((area, ref, fp, local))
    else:
        obstacles.append(bb)

# add forced pull-ups as fixed obstacles for the rest of the pack
for ref, spec in forced_positions.items():
    fp = fps[ref]
    local = local_cy(fp)
    pos = pcbnew.VECTOR2I(int(spec['x']*1e6), int(spec['y']*1e6))
    rect = bbox_at(local, pos, spec['angle'])
    obstacles.append((int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])))

# cutout areas (no placement)
obstacles.append((int(2.08e6), int(81.56e6), int(23.08e6), int(94.56e6)))
obstacles.append((int(13.08e6), int(86.06e6), int(19.08e6), int(94.56e6)))
obstacles.append((int(60.08e6), int(85.56e6), int(77.08e6), int(94.56e6)))

MARGIN = int(1.0e6)  # board edge margin
MAX_X = int(100e6); MAX_Y = int(120e6)
PLACEMENT_MARGIN = int(0.8e6)

def inside(rect):
    return rect[0] > MARGIN and rect[1] > MARGIN and rect[2] < MAX_X - MARGIN and rect[3] < MAX_Y - MARGIN

xs = [round(i*1.27e6) for i in range(2, 77)]
ys_top = [round(i*1.27e6) for i in range(75, 94)]

placed_obstacles = obstacles.copy()
placements = {}

# seed forced pull-up positions
for ref, spec in forced_positions.items():
    fp = fps[ref]
    local = local_cy(fp)
    pos = pcbnew.VECTOR2I(int(spec['x']*1e6), int(spec['y']*1e6))
    rect = bbox_at(local, pos, spec['angle'])
    placements[ref] = spec
    placed_obstacles.append((int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])))
    print(f'Forced {ref} at ({spec["x"]}, {spec["y"]})', file=sys.stderr)

for area, ref, fp, local in sorted(movable_items, key=lambda x: -x[0]):
    done = False
    for angle in (0, 90, 180, 270):
        for x in xs:
            for y in ys_top:
                pos = pcbnew.VECTOR2I(int(x), int(y))
                rect = bbox_at(local, pos, angle)
                if not inside(rect):
                    continue
                collision = False
                for obs in placed_obstacles:
                    if overlaps(rect, obs, margin=PLACEMENT_MARGIN):
                        collision = True
                        break
                if collision:
                    continue
                placements[ref] = {'x': x/1e6, 'y': y/1e6, 'angle': angle}
                placed_obstacles.append((int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])))
                done = True
                print(f'Placed {ref} at ({x/1e6:.2f}, {y/1e6:.2f}) angle {angle}', file=sys.stderr)
                break
            if done: break
        if done: break
    if not done:
        print(f'FAIL to place {ref}', file=sys.stderr)

with open(OUT, 'w') as f:
    json.dump(placements, f, indent=2)
print('Wrote', OUT, file=sys.stderr)
