#!/usr/bin/env python3
"""Safe GND via + zone fix for nebula_qshield.

This script starts from a KiCad 9 board and does the following:
  * Removes known dangling 3V3_RAIL stubs from earlier routing attempts.
  * Sets In1.Cu and B.Cu GND zones to ZONE_CONNECTION_FULL with local
    clearance 0.0 (undoing the 0.5 mm gap that isolated v8 GND vias).
  * Creates a full-board B.Cu GND zone if it is missing.
  * Sets In2.Cu power zones to ZONE_CONNECTION_FULL with thermal spokes.
  * Removes and re-creates GND vias so they keep their F.Cu/B.Cu pads.
  * Drops a 0.6/0.3 mm GND via on every SMD GND pad whose centre is clear
    of B.Cu non-GND copper by at least 0.65 mm.
  * Fills zones and saves the board.

This is the safe baseline PR: it does not add manual F.Cu tracks, so it
introduces no new copper violations. Manual F.Cu routes for the remaining
unconnected GND clusters will be handled in a follow-up.
"""
import sys
import math
import pcbnew

MM = 1_000_000

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


def build_bcu_obstacles(board):
    obstacles = []
    for t in board.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            if t.GetNetname() != "GND" and t.GetLayerSet().Contains(pcbnew.B_Cu):
                pos = t.GetPosition()
                r = t.GetWidth(pcbnew.B_Cu) / 2.0 / 1e6
                obstacles.append((pos.x / 1e6, pos.y / 1e6, r))
        elif isinstance(t, pcbnew.PCB_TRACK):
            if t.GetLayer() == pcbnew.B_Cu and t.GetNetname() != "GND":
                s = t.GetStart()
                e = t.GetEnd()
                obstacles.append((s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6, t.GetWidth() / 2.0 / 1e6))
    return obstacles


def distance_to_obstacle(x, y, obstacles, safe=0.65):
    for obs in obstacles:
        if len(obs) == 3:
            vx, vy, r = obs
            d = math.hypot(x - vx, y - vy)
        else:
            x1, y1, x2, y2, r = obs
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
        if d < safe + r:
            return d
    return None


def reset_gnd_vias(board, net):
    # Remove existing GND vias and let place_gnd_vias recreate them with
    # SetRemoveUnconnected(False) so F.Cu/B.Cu pads are kept.
    for t in list(board.GetTracks()):
        if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND":
            board.Delete(t)


def place_gnd_vias(board, net, obstacles, safe=0.65):
    existing = set()
    for t in board.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA) and t.GetNetname() == "GND":
            pos = t.GetPosition()
            existing.add((round(pos.x / 1e6, 3), round(pos.y / 1e6, 3)))

    for fp in board.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() != "GND" or p.GetAttribute() != 1:
                continue
            pos = p.GetPosition()
            x = pos.x / 1e6
            y = pos.y / 1e6
            if x < 0 or x > 100 or y < 0 or y > 100:
                continue
            if (round(x, 3), round(y, 3)) in existing:
                continue
            if distance_to_obstacle(x, y, obstacles, safe) is None:
                add_via(board, net, (x, y))


def setup_zones(board, net):
    # In1.Cu GND: full connection, zero clearance so vias connect to the plane
    for z in board.Zones():
        if z.GetNetname() == "GND" and board.GetLayerName(z.GetLayer()) == "In1.Cu":
            set_zone_full(z, clearance_um=0, island_um=10 * MM * MM)
            z.SetDoNotAllowVias(False)
            z.SetDoNotAllowPads(False)

    # B.Cu GND: create if missing, zero clearance, large island area
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

    # In2.Cu power zones: full connection, keep existing clearance
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

    obstacles = build_bcu_obstacles(board)
    reset_gnd_vias(board, net_gnd)
    place_gnd_vias(board, net_gnd, obstacles, safe=0.65)

    fill_zones(board)
    board.BuildConnectivity()
    pcbnew.SaveBoard(BOARD_PATH, board)
    print(f"Saved {BOARD_PATH}")


if __name__ == "__main__":
    main()
