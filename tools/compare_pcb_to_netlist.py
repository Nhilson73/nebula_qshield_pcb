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
        for node in net.findall('node'):
            ref = node.get('ref')
            pin = node.get('pin')
            nets.setdefault(ref, {})[pin] = name
    return nets


def main():
    netlist_nets = parse_netlist(NETLIST)
    board = pcbnew.LoadBoard(str(PCB))
    mismatches = []
    missing_fp = []
    for fp in board.Footprints():
        ref = fp.GetReference()
        if ref not in netlist_nets:
            continue
        fp_nets = netlist_nets[ref]
        for pad in fp.Pads():
            pin = str(pad.GetNumber())
            expected = fp_nets.get(pin)
            if expected is None:
                continue
            actual = pad.GetNetname()
            if actual != expected:
                mismatches.append((ref, pin, actual, expected))
        # Check for extra pads in netlist not present on footprint?
    for ref in netlist_nets:
        if not board.FindFootprintByReference(ref):
            missing_fp.append(ref)
    print('Missing footprints:', missing_fp)
    print('Net mismatches (total):', len(mismatches))
    for ref, pin, actual, expected in mismatches[:50]:
        print(f'  {ref} pin {pin}: {actual} -> {expected}')
    if len(mismatches) > 50:
        print(f'  ... and {len(mismatches)-50} more')


if __name__ == '__main__':
    main()
