#!/usr/bin/env python3
"""Manual GND routing for nebula_qshield.

This script:
  * Removes known dangling 3V3_RAIL stubs.
  * Sets GND zones to ZONE_CONNECTION_FULL with zero clearance.
  * Ensures a full-board B.Cu GND zone exists.
  * Reroutes /Power Management/EN_UVLO on B.Cu to clear the U3 GND pad.
  * Removes existing GND vias and recreates them with SetRemoveUnconnected(False).
  * Places 0.6/0.3 mm GND vias on SMD GND pads, using a per-net clearance.
  * Tries centre placement first, then searches an offset grid inside/overlapping
    the pad.
  * Adds a manual F.Cu track from R35 pin 2 to U3 pin 2 (GND).
  * Fills zones and saves.
"""
import sys
import math
import pcbnew

MM = 1_000_000
VIA_RAD = 0.3
STEP = 0.05

BOARD_PATH = sys.argv[1] if len(sys.argv) > 1 else "/workspace/kicad/nebula_qshield.kicad_pcb"


def mm(v):
    return int(v * MM)


def v(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def set_zone_full(zone, clearance_um=None, island_um=None):
    zone.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    zone.SetThermalReliefGap(mm(0.2))
    zone.SetThermalReliefSpokeWidth(mm(0.2))
    if clearance_um is not None:
        zone.SetLocalClearance(clearance_um)
    if island_um is not None:
        zone.SetMinIslandArea(island_um)


def add_track(board, net, layer, start, end, width=0.25):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(v(*start))
    t.SetEnd(v(*end))
    t.SetLayer(layer)
    t.SetWidth(mm(width))
    t.SetNet(net)
    board.Add(t)
    return t


def add_via(board, net, pos, drill=0.3, dia=0.6):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(v(*pos))
    via.SetDrill(mm(drill))
    via.SetWidth(mm(dia))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    via.SetKeepStartEnd(False)
    via.SetRemoveUnconnected(False)
    via.SetNet(net)
    board.Add(via)
    return via


def remove_stubs(board):
    stubs = (
        "6634325a-fbe9-47e2-a9b7-4247bc9d466b",
        "a8060a43-02a3-47e3-9e0a-06d0234827b4",
    )
    for t in list(board.GetTracks()):
        if t.m_Uuid.AsString() in stubs:
            board.Delete(t)


def net_clearance(board, net_name):
    """Return the conservative clearance for a net (mm)."""
    net = board.FindNet(net_name)
    if net is None:
        return 0.2
    names = [n.strip() for n in net.GetNetClassName().split(",") if n.strip()]
    ncs = board.GetNetClasses()
    clear = 0.2
    for n in names:
        if n in ncs:
            c = ncs[n].GetClearance() / MM
        else:
            c = 0.2
        if c > clear:
            clear = c
    return clear


def get_pad_rect(p):
    bb = p.GetBoundingBox()
    return (bb.GetX() / MM, bb.GetY() / MM, (bb.GetX() + bb.GetWidth()) / MM, (bb.GetY() + bb.GetHeight()) / MM)


def rect_dist(px, py, r):
    x1, y1, x2, y2 = r
    dx = max(max(x1 - px, 0), px - x2)
    dy = max(max(y1 - py, 0), py - y2)
    return math.hypot(dx, dy)


def build_layer_obstacles(board, layer_id):
    """Build obstacles on a single external copper layer for non-GND copper.

    Returns a list of tuples:
      - via/round: (x, y, r, safe)
      - track:     (x1, y1, x2, y2, r, safe)
      - pad rect:  (x1, y1, x2, y2, safe)
    safe = VIA_RAD + net clearance of the obstacle.
    """
    obstacles = []
    for t in board.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            if not t.GetLayerSet().Contains(layer_id):
                continue
            if t.GetNetname() == "GND":
                continue
            r = t.GetWidth(layer_id) / 2.0 / MM
            safe = VIA_RAD + net_clearance(board, t.GetNetname())
            obstacles.append((t.GetPosition().x / MM, t.GetPosition().y / MM, r, safe))
        elif isinstance(t, pcbnew.PCB_TRACK):
            if t.GetLayer() != layer_id:
                continue
            if t.GetNetname() == "GND":
                continue
            r = t.GetWidth() / 2.0 / MM
            safe = VIA_RAD + net_clearance(board, t.GetNetname())
            obstacles.append((t.GetStart().x / MM, t.GetStart().y / MM, t.GetEnd().x / MM, t.GetEnd().y / MM, r, safe))

    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == "GND":
                continue
            if not p.GetLayerSet().Contains(layer_id):
                continue
            safe = VIA_RAD + net_clearance(board, p.GetNetname())
            obstacles.append(get_pad_rect(p) + (safe,))
    return obstacles


def build_bcu_obstacles(board):
    return build_layer_obstacles(board, pcbnew.B_Cu)


def build_fcu_obstacles(board):
    return build_layer_obstacles(board, pcbnew.F_Cu)


def distance_to_obstacle(x, y, obstacles):
    """Return None if safe, or the worst negative margin if blocked."""
    min_margin = float("inf")
    for obs in obstacles:
        if len(obs) == 4:
            # via / round pad
            vx, vy, r, safe = obs
            d = math.hypot(x - vx, y - vy)
            margin = d - safe - r
        elif len(obs) == 5:
            # rectangular pad
            x1, y1, x2, y2, safe = obs
            d = rect_dist(x, y, (x1, y1, x2, y2))
            margin = d - safe
        else:
            # track
            x1, y1, x2, y2, r, safe = obs
            dx = x2 - x1
            dy = y2 - y1
            seg = math.hypot(dx, dy)
            if seg == 0:
                d = math.hypot(x - x1, y - y1)
            else:
                t = ((x - x1) * dx + (y - y1) * dy) / seg / seg
                t = max(0.0, min(1.0, t))
                cx = x1 + t * dx
                cy = y1 + t * dy
                d = math.hypot(x - cx, y - cy)
            margin = d - safe - r
        if margin < min_margin:
            min_margin = margin
            if margin < 0:
                return margin
    return None if min_margin >= 0 else min_margin


def move_en_uvlo(board):
    """Reroute /Power Management/EN_UVLO to clear the U3 and R35 GND pads.

    The B.Cu route is rerouted away from U3 pad 2.  The F.Cu route from R35-1
    to the via at (7.8078, 24.3586) is raised to y=24.5 so a 0.6 mm GND via
    can be placed on R35-2 at (8.34, 23.62).
    """
    en_net = board.FindNet("/Power Management/EN_UVLO")
    if en_net is None:
        print("EN_UVLO net not found, skipping reroute")
        return

    # Remove B.Cu EN_UVLO tracks; keep vias and F.Cu tracks.
    for t in list(board.GetTracks()):
        if isinstance(t, pcbnew.PCB_TRACK) and not isinstance(t, pcbnew.PCB_VIA) and t.GetLayer() == pcbnew.B_Cu and t.GetNetname() == "/Power Management/EN_UVLO":
            board.Delete(t)

    b_pts = [
        (7.8078, 24.3586),
        (7.3, 24.3586),
        (7.3, 22.0),
        (7.8078, 21.1057),
        (6.9681, 20.266),
        (6.4246, 20.266),
        (6.4246, 19.5),
        (4.6, 19.5),
        (4.6, 22.1546),
        (4.536, 22.1546),
        (3.602, 22.1546),
        (3.2476, 21.8002),
        (3.2476, 15.8789),
    ]
    for (x1, y1), (x2, y2) in zip(b_pts, b_pts[1:]):
        add_track(board, en_net, pcbnew.B_Cu, (x1, y1), (x2, y2), width=0.25)

    # Reroute the F.Cu EN_UVLO branch near R35 so R35-2 can take a GND via.
    for t in list(board.GetTracks()):
        if isinstance(t, pcbnew.PCB_TRACK) and not isinstance(t, pcbnew.PCB_VIA) and t.GetLayer() == pcbnew.F_Cu and t.GetNetname() == "/Power Management/EN_UVLO":
            x1, y1 = t.GetStart().x / MM, t.GetStart().y / MM
            x2, y2 = t.GetEnd().x / MM, t.GetEnd().y / MM
            # Delete the R35-pad1 -> via branch; keep the U1 branch at lower left.
            if x1 > 6.0 and x2 > 6.0 and y1 > 23.0 and y2 > 23.0:
                board.Delete(t)

    # R34-2 -> R35-1 -> via, lifted above the R35-2 GND pad.
    r34 = board.FindFootprintByReference("R34")
    r35 = board.FindFootprintByReference("R35")
    r34_p2 = r34.FindPadByNumber("2") if r34 else None
    r35_p1 = r35.FindPadByNumber("1") if r35 else None
    r34_pos = r34_p2.GetPosition() if r34_p2 else None
    r35_pos = r35_p1.GetPosition() if r35_p1 else None
    if r34_pos and r35_pos:
        add_track(board, en_net, pcbnew.F_Cu, (r34_pos.x / MM, r34_pos.y / MM), (r35_pos.x / MM, r35_pos.y / MM))
    add_track(board, en_net, pcbnew.F_Cu, (7.32, 23.62), (7.32, 24.5))
    add_track(board, en_net, pcbnew.F_Cu, (7.32, 24.5), (7.8078, 24.5))
    add_track(board, en_net, pcbnew.F_Cu, (7.8078, 24.5), (7.8078, 24.3586))


def reset_gnd_vias(board, net):
    for t in list(board.GetTracks()):
        if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND":
            board.Delete(t)


def place_gnd_vias(board, net, bcu, fcu):
    """Place a 0.6/0.3 mm GND via on every SMD GND pad that can accept one.

    Tries the pad centre first, then searches an offset grid.  Uses per-net
    clearances and dynamically adds placed vias as obstacles to avoid
    via-to-via violations.
    """
    existing = set()
    for t in board.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND":
            existing.add((round(t.GetPosition().x / MM, 3), round(t.GetPosition().y / MM, 3)))

    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() != "GND" or p.GetAttribute() != 1:
                continue
            rect = get_pad_rect(p)
            cx = (rect[0] + rect[2]) / 2.0
            cy = (rect[1] + rect[3]) / 2.0
            if cx < 0.55 or cx > 99.45 or cy < 0.55 or cy > 99.45:
                continue
            if (round(cx, 3), round(cy, 3)) in existing:
                continue

            placed = False
            # Try centre first
            if rect_dist(cx, cy, rect) <= VIA_RAD and distance_to_obstacle(cx, cy, bcu) is None and distance_to_obstacle(cx, cy, fcu) is None:
                via = add_via(board, net, (cx, cy))
                existing.add((round(cx, 3), round(cy, 3)))
                bcu.append((cx, cy, VIA_RAD, VIA_RAD + net_clearance(board, "GND")))
                fcu.append((cx, cy, VIA_RAD, VIA_RAD + net_clearance(board, "GND")))
                placed = True
            else:
                nx = int((rect[2] - rect[0] + 2 * VIA_RAD) / STEP) + 2
                ny = int((rect[3] - rect[1] + 2 * VIA_RAD) / STEP) + 2
                for i in range(-nx, nx + 1):
                    x = cx + i * STEP
                    for j in range(-ny, ny + 1):
                        y = cy + j * STEP
                        if x < 0.55 or x > 99.45 or y < 0.55 or y > 99.45:
                            continue
                        if rect_dist(x, y, rect) > VIA_RAD:
                            continue
                        if (round(x, 3), round(y, 3)) in existing:
                            continue
                        if distance_to_obstacle(x, y, bcu) is not None:
                            continue
                        if distance_to_obstacle(x, y, fcu) is not None:
                            continue
                        via = add_via(board, net, (x, y))
                        existing.add((round(x, 3), round(y, 3)))
                        bcu.append((x, y, VIA_RAD, VIA_RAD + net_clearance(board, "GND")))
                        fcu.append((x, y, VIA_RAD, VIA_RAD + net_clearance(board, "GND")))
                        placed = True
                        break
                    if placed:
                        break
            if not placed:
                print(f"No safe via for {fp.GetReference()}-{p.GetNumber()} at ({cx}, {cy})")


def setup_zones(board, net):
    for z in board.Zones():
        if z.GetNetname() == "GND" and board.GetLayerName(z.GetLayer()) == "In1.Cu":
            set_zone_full(z, clearance_um=0, island_um=10 * MM * MM)
            z.SetDoNotAllowVias(False)
            z.SetDoNotAllowPads(False)

    has_b_gnd = False
    for z in board.Zones():
        if z.GetNetname() == "GND" and board.GetLayerName(z.GetLayer()) == "B.Cu":
            has_b_gnd = True
            set_zone_full(z, clearance_um=0, island_um=10 * MM * MM)
            z.SetDoNotAllowVias(False)
            z.SetDoNotAllowPads(False)
    if not has_b_gnd:
        zone = pcbnew.ZONE(board)
        zone.SetLayer(pcbnew.B_Cu)
        zone.SetNet(net)
        out = zone.Outline()
        out.RemoveAllContours()
        out.NewOutline()
        out.Append(0, 0)
        out.Append(mm(100), 0)
        out.Append(mm(100), mm(100))
        out.Append(0, mm(100))
        set_zone_full(zone, clearance_um=0, island_um=10 * MM * MM)
        zone.SetDoNotAllowVias(False)
        zone.SetDoNotAllowPads(False)
        board.Add(zone)

    for z in board.Zones():
        if z.GetNetname() in ("/3V3_RAIL", "/5V_RAIL", "/12V_RAIL") and board.GetLayerName(z.GetLayer()) == "In2.Cu":
            set_zone_full(z, clearance_um=None, island_um=10 * MM * MM)


def fill_zones(board):
    zones = list(board.Zones())
    if zones:
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(zones)


def main():
    board = pcbnew.LoadBoard(BOARD_PATH)
    net_gnd = board.FindNet("GND")
    if net_gnd is None:
        raise RuntimeError("GND net not found")

    remove_stubs(board)
    setup_zones(board, net_gnd)
    move_en_uvlo(board)

    reset_gnd_vias(board, net_gnd)
    bcu = build_bcu_obstacles(board)
    fcu = build_fcu_obstacles(board)
    place_gnd_vias(board, net_gnd, bcu, fcu)

    fill_zones(board)
    board.BuildConnectivity()
    pcbnew.SaveBoard(BOARD_PATH, board)
    print(f"Saved {BOARD_PATH}")


if __name__ == "__main__":
    main()
