#!/usr/bin/env python3
"""Generate the initial .kicad_pcb layout for nebula_qshield.

Run inside the kicad/kicad:9.0 container:
    python3 tools/generate_initial_layout.py

Assumes /workspace is the repo root and netlist.xml has been generated.
"""
import math
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew

MM = 1_000_000
BOARD_W = 100
BOARD_H = 100
CORNER_R = 2.5
SPACING = 0.125

# Layer IDs
EDGE_CUTS = pcbnew.Edge_Cuts
F_CU = pcbnew.F_Cu
B_CU = pcbnew.B_Cu
IN1_CU = pcbnew.In1_Cu
IN2_CU = pcbnew.In2_Cu
F_CRTYD = pcbnew.F_CrtYd

REPO = Path(__file__).resolve().parent.parent
NETLIST = REPO / 'netlist.xml'
OUT_PCB = REPO / 'kicad' / 'nebula_qshield.kicad_pcb'
CUSTOM_FP = REPO / 'kicad' / 'lib' / 'nebula_footprints.pretty'
STD_FP = Path('/usr/share/kicad/footprints')


def nm(v: float) -> int:
    return int(round(v * MM))


def load_netlist(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    components = []
    for comp in root.findall('components/comp'):
        ref = comp.get('ref')
        value = comp.find('value').text or ''
        footprint = comp.find('footprint').text or ''
        sheet = ''
        prop = comp.find('property[@name="Sheetname"]')
        if prop is not None:
            sheet = prop.get('value')
        components.append({
            'ref': ref,
            'value': value,
            'footprint': footprint,
            'sheet': sheet,
        })
    pad_net = {}
    for net in root.findall('nets/net'):
        name = net.get('name')
        for node in net.findall('node'):
            key = (node.get('ref'), node.get('pin'))
            pad_net[key] = name
    return components, pad_net


def resolve_fp_path(name: str):
    if not name:
        return None, None
    if ':' in name:
        lib, fp = name.split(':', 1)
    else:
        lib, fp = '', name
    if lib == 'nebula_footprints':
        return str(CUSTOM_FP), fp
    if lib:
        return str(STD_FP / f'{lib}.pretty'), fp
    return None, fp


def load_footprint(name: str):
    lib, fp = resolve_fp_path(name)
    if not lib:
        return None
    try:
        return pcbnew.FootprintLoad(lib, fp)
    except Exception:
        return None


def bbox_at(fp, x, y, rot=0, inflate=0.0):
    """Return absolute bounding box for a footprint placed at (x,y,rot).

    Uses pads plus F.CrtYd only, so the bottom-side board outline in J21 is
    ignored for placement.
    """
    old_pos = fp.GetPosition()
    old_rot = fp.GetOrientation()
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.TENTHS_OF_A_DEGREE_T))
    fp.SetPosition(pcbnew.VECTOR2I(nm(x), nm(y)))
    bb = pcbnew.BOX2I()
    first = True
    for pad in fp.Pads():
        pb = pad.GetBoundingBox()
        if first:
            bb = pb
            first = False
        else:
            bb.Merge(pb)
    for gi in fp.GraphicalItems():
        if gi.GetLayer() == F_CRTYD:
            gb = gi.GetBoundingBox()
            if first:
                bb = gb
                first = False
            else:
                bb.Merge(gb)
    if first:
        bb = pcbnew.BOX2I(pcbnew.VECTOR2I(0, 0), pcbnew.VECTOR2I(0, 0))
    if inflate:
        bb.Inflate(nm(inflate))
    fp.SetPosition(old_pos)
    fp.SetOrientation(old_rot)
    return bb


def placement_box(fp, rot=0, inflate=0.0):
    """Return a local bounding box (footprint at origin)."""
    return bbox_at(fp, 0, 0, rot, inflate)


def abs_box(fp, x, y, rot=0):
    return bbox_at(fp, x, y, rot, SPACING)


def boxes_intersect(a, b):
    return a.GetLeft() < b.GetRight() and a.GetRight() > b.GetLeft() and \
           a.GetTop() < b.GetBottom() and a.GetBottom() > b.GetTop()


def box_inside_board(bb, margin=0.0):
    return bb.GetLeft() >= nm(margin) and bb.GetRight() <= nm(BOARD_W - margin) and \
           bb.GetTop() >= nm(margin) and bb.GetBottom() <= nm(BOARD_H - margin)


STEP = 0.25

def find_position(fp, zone, used_boxes, rot=0):
    """Greedy top-left scan. Returns (x,y) or None."""
    bb = placement_box(fp, rot, SPACING)
    w = bb.GetWidth() / MM
    h = bb.GetHeight() / MM
    zl, zt, zr, zb = zone
    steps_x = int(math.floor((zr - zl - w) / STEP)) + 1
    steps_y = int(math.floor((zb - zt - h) / STEP)) + 1
    if steps_x <= 0 or steps_y <= 0:
        return None
    for iy in range(steps_y):
        for ix in range(steps_x):
            x = zl + ix * STEP + (bb.GetLeft() / -MM)
            y = zt + iy * STEP + (bb.GetTop() / -MM)
            cand = abs_box(fp, x, y, rot)
            if not box_inside_board(cand):
                continue
            overlap = False
            for ub in used_boxes:
                if boxes_intersect(cand, ub):
                    overlap = True
                    break
            if not overlap:
                return x, y
    return None


def add_zone(board, net, layer, pts, priority=0):
    """Add a filled polygonal zone."""
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetIsFilled(True)
    z.SetFillMode(0)
    z.SetAssignedPriority(priority)
    z.SetMinThickness(nm(0.25))
    z.SetThermalReliefGap(nm(0.5))
    z.SetThermalReliefSpokeWidth(nm(0.5))
    lc = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in pts:
        lc.Append(pcbnew.VECTOR2I(nm(x), nm(y)), False)
    lc.SetClosed(True)
    z.Outline().AddOutline(lc)
    board.Add(z)
    return z


def rounded_edge_cuts(board, w, h, r):
    pts = []
    def arc(cx, cy, radius, start, end, steps=8):
        for i in range(steps + 1):
            a = start + (end - start) * i / steps
            # KiCad y is down, so negate sin
            pts.append((cx + radius * math.cos(a), cy - radius * math.sin(a)))
    # order clockwise; start top-left interior corner
    arc(r, r, r, math.pi, math.pi / 2)
    arc(w - r, r, r, math.pi / 2, 0)
    arc(w - r, h - r, r, 0, -math.pi / 2)
    arc(r, h - r, r, -math.pi / 2, -math.pi)
    shape = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_POLY)
    lc = pcbnew.SHAPE_LINE_CHAIN()
    for x, y in pts:
        lc.Append(pcbnew.VECTOR2I(nm(x), nm(y)), False)
    lc.SetClosed(True)
    ps = pcbnew.SHAPE_POLY_SET()
    ps.AddOutline(lc)
    shape.SetPolyShape(ps)
    shape.SetLayer(EDGE_CUTS)
    shape.SetWidth(0)
    board.Add(shape)


def create_board():
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    board.SetLayerType(IN1_CU, pcbnew.LT_POWER)
    board.SetLayerType(IN2_CU, pcbnew.LT_POWER)
    rounded_edge_cuts(board, BOARD_W, BOARD_H, CORNER_R)
    return board


def add_nets(board, components, pad_net):
    """Create NETINFO_ITEM for every net referenced in the netlist."""
    net_names = set()
    for comp in components:
        ref = comp['ref']
        for pin in [node[1] for node in pad_net if node[0] == ref]:
            net_names.add(pad_net[(ref, pin)])
    for name in sorted(net_names):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)


def add_copper_zones(board, j21_x, j21_y):
    # GND plane on In1.Cu
    gnd = board.FindNet('GND')
    if gnd:
        add_zone(board, gnd, IN1_CU, [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)], 0)

    # Power nets on In2.Cu
    v12 = board.FindNet('/12V_RAIL')
    v5 = board.FindNet('/5V_RAIL')
    v3 = board.FindNet('/3V3_RAIL')

    if v12:
        # 12V fills the board as the lowest priority background
        add_zone(board, v12, IN2_CU, [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)], 1)

    if v5:
        # 5V islands: Power left (U2), Digital zone, Analog left (U4-U13 isolated side)
        add_zone(board, v5, IN2_CU, [(10, 0), (25, 0), (25, 59.7), (10, 59.7)], 2)
        add_zone(board, v5, IN2_CU, [(25.02, 0), (55, 0), (55, 59.7), (25.02, 59.7)], 3)
        add_zone(board, v5, IN2_CU, [(55, 0), (75, 0), (75, 36.025), (55, 36.025)], 4)

    if v3:
        # 3V3 islands: Analog right (low side) + Power left (U3)
        add_zone(board, v3, IN2_CU, [(75, 0), (100, 0), (100, 35), (75, 35)], 5)
        add_zone(board, v3, IN2_CU, [(20, 0), (25, 0), (25, 59.7), (20, 59.7)], 6)

    # Small J21 pin planes
    if v12:
        # J21 pin 7 (12V)
        add_zone(board, v12, IN2_CU, [
            (j21_x - 2.5, j21_y + 13.5),
            (j21_x + 2.5, j21_y + 13.5),
            (j21_x + 2.5, j21_y + 18.5),
            (j21_x - 2.5, j21_y + 18.5),
        ], 7)

    if v5:
        # J21 pin 10 (5V)
        add_zone(board, v5, IN2_CU, [
            (j21_x - 2.5, j21_y + 21.5),
            (j21_x + 2.5, j21_y + 21.5),
            (j21_x + 2.5, j21_y + 25.0),
            (j21_x - 2.5, j21_y + 25.0),
        ], 8)

    if v3:
        # J21 pin 11 (3V3)
        add_zone(board, v3, IN2_CU, [
            (j21_x - 2.5, j21_y + 25.5),
            (j21_x + 2.5, j21_y + 25.5),
            (j21_x + 2.5, j21_y + 28.5),
            (j21_x - 2.5, j21_y + 28.5),
        ], 9)


def preplace_connector(ref, fp, pos, used, rot=0):
    fp.SetReference(ref)
    fp.SetValue(ref)
    fp.SetLayer(F_CU)
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.TENTHS_OF_A_DEGREE_T))
    fp.SetPosition(pcbnew.VECTOR2I(nm(pos[0]), nm(pos[1])))
    cand = abs_box(fp, pos[0], pos[1], rot)
    for ub in used:
        if boxes_intersect(cand, ub):
            print(f'WARN: connector {ref} overlaps a pre-placed footprint at {pos}')
    used.append(cand)


def preplace_component(components, ref, pos, used, rot=0):
    comp = next((c for c in components if c['ref'] == ref), None)
    if not comp:
        return None
    fp = load_footprint(comp['footprint'])
    if fp is None:
        print(f'WARN: cannot load preplaced component {ref}')
        return None
    fp.SetReference(ref)
    fp.SetValue(comp['value'])
    fp.SetLayer(F_CU)
    fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.TENTHS_OF_A_DEGREE_T))
    fp.SetPosition(pcbnew.VECTOR2I(nm(pos[0]), nm(pos[1])))
    cand = abs_box(fp, pos[0], pos[1], rot)
    for ub in used:
        if boxes_intersect(cand, ub):
            print(f'WARN: preplaced {ref} overlaps at {pos}')
    used.append(cand)
    return fp


def place_component(board, comp, zone, used_boxes, fp=None):
    if fp is None:
        fp = load_footprint(comp['footprint'])
    if fp is None:
        print(f'WARN: cannot load {comp["ref"]} {comp["footprint"]}')
        return None
    fp.SetReference(comp['ref'])
    fp.SetValue(comp['value'])
    fp.SetLayer(F_CU)

    best_pos = None
    best_rot = None
    for rot in [0, 900]:
        pos = find_position(fp, zone, used_boxes, rot)
        if pos:
            if best_pos is None or pos[1] > best_pos[1] or (pos[1] == best_pos[1] and pos[0] < best_pos[0]):
                best_pos = pos
                best_rot = rot
    if best_pos is None:
        print(f'WARN: cannot place {comp["ref"]} in zone {zone}')
        return None
    fp.SetOrientation(pcbnew.EDA_ANGLE(best_rot, pcbnew.TENTHS_OF_A_DEGREE_T))
    fp.SetPosition(pcbnew.VECTOR2I(nm(best_pos[0]), nm(best_pos[1])))
    used_boxes.append(abs_box(fp, best_pos[0], best_pos[1], best_rot))
    board.Add(fp)
    return fp


def assign_nets(board, fp, pad_net):
    for pad in fp.Pads():
        num = pad.GetNumber()
        key = (fp.GetReference(), num)
        if key in pad_net:
            net = board.FindNet(pad_net[key])
            if net:
                pad.SetNet(net)


def main():
    components, pad_net = load_netlist(NETLIST)
    board = create_board()
    add_nets(board, components, pad_net)

    # J21 fixed first
    j21_x = (BOARD_W - 48.26) / 2
    j21_y = 100 - 39.25
    j21 = load_footprint('nebula_footprints:Arduino_UNO_Shield_2x20')
    if j21 is None:
        raise RuntimeError('Cannot load J21 footprint')
    j21.SetReference('J21')
    j21.SetValue('J21')
    j21.SetLayer(F_CU)
    j21.SetOrientation(pcbnew.EDA_ANGLE(0, pcbnew.TENTHS_OF_A_DEGREE_T))
    j21.SetPosition(pcbnew.VECTOR2I(nm(j21_x), nm(j21_y)))
    board.Add(j21)

    used_boxes = [abs_box(j21, j21_x, j21_y, 0)]

    # Pre-place edge connectors
    connectors = [
        ('J1',  (0, 2.0), 0),
        ('J2',  (98.4, 6.0), 0),
        ('J3',  (98.4, 18.55), 0),
        ('J5',  (98.4, 31.15), 0),
        ('J4',  (55.0, 1.3), 0),
        ('J6',  (67.0, 1.3), 0),
        ('J7',  (80.0, 1.3), 0),
        ('J20', (41.0, 1.3), 0),
        ('J14', (50.0, 25.0), 0),
        ('J15', (98.4, 42.7), 0),
        ('J16', (98.4, 53.25), 0),
        ('J17', (98.4, 63.8), 0),
        ('J18', (98.4, 74.35), 0),
        ('J19', (98.4, 84.9), 0),
        ('J8',  (28.0, 9.0), 0),
        ('J9',  (37.0, 9.0), 0),
        ('J10', (46.0, 9.0), 0),
        ('J11', (46.0, 16.0), 0),
        ('J12', (36.25, 16.0), 0),
        ('J13', (28.0, 16.0), 0),
    ]
    fp_by_ref = {}
    for ref, pos, rot in connectors:
        comp = next((c for c in components if c['ref'] == ref), None)
        if not comp:
            continue
        fp = load_footprint(comp['footprint'])
        if fp is None:
            print(f'WARN: cannot load connector {ref}')
            continue
        preplace_connector(ref, fp, pos, used_boxes, rot)
        board.Add(fp)
        fp_by_ref[ref] = fp

    # Pre-place specific large Actuator components to create a good initial layout
    preplaced_comps = [
        ('U16', (34.0, 45.0), 0),
        ('Q1',  (82.05, 56.215), 900),
        ('Q2',  (87.3, 56.215), 900),
        ('Q5',  (92.55, 56.215), 900),
        ('D14', (85.025, 46.175), 0),
    ]
    for ref, pos, rot in preplaced_comps:
        fp = preplace_component(components, ref, pos, used_boxes, rot)
        if fp:
            board.Add(fp)
            fp_by_ref[ref] = fp

    # Add copper zones after J21 is known
    add_copper_zones(board, j21_x, j21_y)

    # Zones for remaining components
    zones = {
        'Power Management':       (0.0, 0.0, 24.52, 59.7),
        'Analog Acquisition':     (55.0, 0.0, 100.0, 36.025),
        'Digital & I2C':          (25.02, 0.0, 55.0, 59.7),
        'Actuator Drivers':       (55.0, 36.025, 96.975, 59.7),
        'HMI & Connectors':       (25.02, 0.0, 55.0, 59.7),  # only J20/J21 are pre-placed
    }

    placed_refs = {'J21'} | {r for r, _, _ in connectors} | {r for r, _, _ in preplaced_comps}
    remaining = []
    for comp in components:
        if comp['ref'] in placed_refs:
            continue
        fp = load_footprint(comp['footprint'])
        if fp is None:
            continue
        bb = placement_box(fp, 0, SPACING)
        w = bb.GetWidth() / MM
        h = bb.GetHeight() / MM
        # Sort by descending height, then width, then area for better packing
        remaining.append((-h, -w, -bb.GetWidth() * bb.GetHeight(), comp, fp))
    remaining.sort(key=lambda x: x[:3])

    for neg_h, neg_w, neg_area, comp, fp in remaining:
        zone = zones.get(comp['sheet'], (25.02, 0.0, 74.98, 59.7))
        fp = place_component(board, comp, zone, used_boxes, fp=fp)
        if fp:
            fp_by_ref[comp['ref']] = fp

    # Assign nets to all pads
    for fp in fp_by_ref.values():
        assign_nets(board, fp, pad_net)
    assign_nets(board, j21, pad_net)

    # Refresh board
    board.BuildListOfNets()
    board.Save(str(OUT_PCB))
    print(f'Saved {OUT_PCB}')


if __name__ == '__main__':
    main()
