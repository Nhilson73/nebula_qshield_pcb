import sys

import pcbnew
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NETLIST = REPO / 'kicad' / 'uno_q.xml'
PCB = REPO / 'kicad' / 'nebula_qshield.kicad_pcb'


def parse_netlist(path):
    tree = ET.parse(path)
    root = tree.getroot()
    nets = {}
    nets_node = root.find('nets')
    for net in nets_node.findall('net'):
        name = net.get('name')
        if name.startswith('unconnected-'):
            continue
        for node in net.findall('node'):
            pintype = node.get('pintype') or ''
            if 'no_connect' in pintype:
                continue
            ref = node.get('ref')
            pin = node.get('pin')
            nets.setdefault(ref, {})[pin] = name
    return nets


def is_real_net(name: str) -> bool:
    """Return True if a pad net name looks like an intentional connection."""
    if not name:
        return False
    if name.startswith('unconnected-'):
        return False
    return True


def main():
    netlist_nets = parse_netlist(NETLIST)
    board = pcbnew.LoadBoard(str(PCB))
    mismatches = []
    stale_nets = []
    missing_pins = []
    missing_fp = []
    extra_fp = []

    board_refs = {fp.GetReference() for fp in board.Footprints()}

    for fp in board.Footprints():
        ref = fp.GetReference()
        if ref not in netlist_nets:
            extra_fp.append(ref)
            continue
        fp_nets = netlist_nets[ref]
        board_pins = {str(p.GetNumber()) for p in fp.Pads()}
        for pin in fp_nets:
            if pin not in board_pins:
                missing_pins.append((ref, pin))
        for pad in fp.Pads():
            pin = str(pad.GetNumber())
            expected = fp_nets.get(pin)
            actual = pad.GetNetname()
            if expected is None:
                # Pin not declared in schematic: any real net on the pad is stale wiring.
                if is_real_net(actual):
                    stale_nets.append((ref, pin, actual))
                continue
            if actual != expected:
                mismatches.append((ref, pin, actual, expected))

    for ref in netlist_nets:
        if ref not in board_refs:
            missing_fp.append(ref)

    total_problems = len(mismatches) + len(stale_nets) + len(missing_pins) + len(missing_fp) + len(extra_fp)
    print('Missing footprints:', missing_fp)
    print('Extra footprints on board (not in schematic):', extra_fp)
    print('Missing pins (in netlist but not footprint):', missing_pins[:20])
    if len(missing_pins) > 20:
        print(f'  ... and {len(missing_pins)-20} more')
    print('Stale nets (pad connected but not declared in schematic):', len(stale_nets))
    for ref, pin, actual in stale_nets[:20]:
        print(f'  {ref} pin {pin}: stale net {actual}')
    if len(stale_nets) > 20:
        print(f'  ... and {len(stale_nets)-20} more')
    print('Net mismatches (total):', len(mismatches))
    for ref, pin, actual, expected in mismatches[:50]:
        print(f'  {ref} pin {pin}: {actual} -> {expected}')
    if len(mismatches) > 50:
        print(f'  ... and {len(mismatches)-50} more')
    print('Total parity problems:', total_problems)
    return 0 if total_problems == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
