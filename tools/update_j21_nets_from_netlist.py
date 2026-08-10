#!/usr/bin/env python3
"""
Assign J21 pad nets directly from the KiCad netlist.

The board netlist may be stale after the UNO Q footprint renumbering; this script
reads the schematic netlist, extracts the J21 pin -> net mapping, and applies it
to the PCB footprint pads.
"""
from pathlib import Path
import re
import sys

REPO = Path(__file__).parent.parent
PCB = REPO / "kicad/nebula_qshield.kicad_pcb"
NET = REPO / "kicad/uno_q.net"


def extract_j21_nets(netlist_path):
    text = netlist_path.read_text()
    pin_to_net = {}
    i = 0
    while True:
        m = re.search(r'\(net\s', text[i:])
        if not m:
            break
        start = i + m.start()
        # find matching close paren for the net block
        depth = 0
        end = start
        while end < len(text):
            if text[end] == '(':
                depth += 1
            elif text[end] == ')':
                depth -= 1
                if depth == 0:
                    end += 1
                    break
            end += 1
        block = text[start:end]
        name_m = re.search(r'\(name\s+"([^"]+)"\)', block)
        if name_m:
            netname = name_m.group(1)
            for node in re.finditer(
                r'\(node\s+\(ref\s+"J21"\)\s+\(pin\s+"(\d+)"\)', block
            ):
                pin_to_net[int(node.group(1))] = netname
        i = end
    return pin_to_net


def resolve_net(board, netname):
    """Find or create a board net matching the schematic netlist name."""
    import pcbnew

    if not netname or netname.startswith("unconnected-"):
        return None

    # Exact match (most common)
    net = board.FindNet(netname)
    if net:
        return net

    # Hierarchical net names may be flattened in the PCB (e.g. /HMI & Connectors/HMI_RX -> /HMI_RX)
    basename = netname.rstrip("/").split("/")[-1]
    if basename:
        for candidate in [f"/{basename}", basename]:
            net = board.FindNet(candidate)
            if net:
                return net
        # Search the board's net list for any net ending with /basename
        ni = board.GetNetInfo()
        for i in range(ni.GetNetCount()):
            cand = ni.GetNetItem(i)
            cname = cand.GetNetname()
            if cname and not cname.startswith("unconnected-") and cname.endswith(f"/{basename}"):
                return cand

    # No existing net; create one so the pad can be assigned
    new_net = pcbnew.NETINFO_ITEM(board, netname)
    board.Add(new_net)
    return new_net


def main():
    import pcbnew

    pin_to_net = extract_j21_nets(NET)
    print(f"Extracted {len(pin_to_net)} J21 pin -> net mappings")

    board = pcbnew.LoadBoard(str(PCB))
    fp = board.FindFootprintByReference("J21")
    if not fp:
        raise RuntimeError("J21 footprint not found")

    for pad in fp.Pads():
        n = pad.GetNumber()
        if not n or not n.isdigit():
            continue
        n = int(n)
        netname = pin_to_net.get(n)
        if not netname or netname.startswith("unconnected-"):
            pad.SetNetCode(0)
            print(f"  pin {n:02d} -> unconnected")
            continue

        net = resolve_net(board, netname)
        if net:
            pad.SetNet(net)
            print(f"  pin {n:02d} -> {net.GetNetname()}")
        else:
            pad.SetNetCode(0)
            print(f"  pin {n:02d} -> unconnected")

    board.Save(str(PCB))
    print(f"Saved {PCB}")


if __name__ == "__main__":
    main()
