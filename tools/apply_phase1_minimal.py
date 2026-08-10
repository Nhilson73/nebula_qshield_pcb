#!/usr/bin/env python3
"""Minimal forward-annotation: update existing nets and insert missing footprints."""
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sexpr

REPO = Path(__file__).resolve().parent.parent
PCB = REPO / 'kicad' / 'nebula_qshield.kicad_pcb'
OUT = REPO / 'kicad' / 'nebula_qshield.kicad_pcb'
NETLIST_XML = REPO / 'kicad' / 'uno_q.xml'
MISSING_PCB = REPO / 'kicad' / 'missing_components.kicad_pcb'
KICAD_SYS_FP = Path('/usr/share/kicad/footprints')

STAGING_START = (45.0, 100.0)
STAGING_DX = 12.0
STAGING_DY = 10.0


def ensure_netlist():
    if not NETLIST_XML.exists():
        subprocess.run(
            ['docker', 'run', '--rm', '-v', f'{REPO}:/workspace',
             'kicad/kicad:10.0.5', 'kicad-cli', 'sch', 'export', 'netlist',
             '--format', 'kicadxml', '-o', '/workspace/kicad/uno_q.xml',
             '/workspace/kicad/nebula_qshield.kicad_sch'],
            check=True,
        )


def parse_netlist_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()
    components = {}
    for comp in root.find('components').findall('comp'):
        ref = comp.get('ref')
        components[ref] = {
            'footprint': comp.findtext('footprint', ''),
            'value': comp.findtext('value', ''),
        }
    ref_pin_net = {}
    for net in root.find('nets').findall('net'):
        name = net.get('name')
        for node in net.findall('node'):
            ref = node.get('ref')
            pin = node.get('pin')
            ref_pin_net.setdefault(ref, {})[pin] = name
    return components, ref_pin_net


def set_at_in_block(block, x, y, angle=0):
    # Replace the footprint-level (at ...) line, not a property.
    # The footprint-level (at) appears before any (property ...) or (pad ...).
    return re.sub(
        r'\(at\s+([\d.\-]+)\s+([\d.\-]+)(?:\s+([\d.\-]+))?\)(?=\n\s*\((?:uuid|descr|tags|property|pad|attr|fp_|model|embedded_fonts|tedit|path|sheetname))',
        f'(at {x:.6f} {y:.6f} {angle})',
        block,
        count=1,
    )


def generate_missing_footprints(missing_refs, components, ref_pin_net):
    if MISSING_PCB.exists():
        MISSING_PCB.unlink()
    placements = {}
    script_lines = [
        'import pcbnew',
        'from pathlib import Path',
        f'KICAD_SYS_FP = Path({str(KICAD_SYS_FP)!r})',
        f'KIPRJMOD = Path("/workspace/kicad")',
        'components = {',
    ]
    for i, ref in enumerate(missing_refs):
        info = components[ref]
        x = STAGING_START[0] + (i % 4) * STAGING_DX
        y = STAGING_START[1] + (i // 4) * STAGING_DY
        placements[ref] = (x, y)
        script_lines.append(f'    {ref!r}: ({info["footprint"]!r}, {info["value"]!r}, ({x}, {y})),')
    script_lines.extend([
        '}',
        'def fp_path(lib):',
        '    proj_dir = KIPRJMOD / "lib" / f"{lib}.pretty"',
        '    if proj_dir.exists():',
        '        return str(proj_dir)',
        '    return str(KICAD_SYS_FP / f"{lib}.pretty")',
        'b = pcbnew.BOARD()',
        'failures = []',
        'for ref, (fp_spec, value, pos) in components.items():',
        '    lib, name = fp_spec.split(":", 1)',
        '    fp = pcbnew.FootprintLoad(fp_path(lib), name)',
        '    if not fp:',
        '        failures.append(fp_spec)',
        '        continue',
        '    fp.SetReference(ref)',
        '    fp.SetValue(value)',
        '    fp.SetPosition(pcbnew.VECTOR2I(int(pos[0] * 1e6), int(pos[1] * 1e6)))',
        '    b.Add(fp)',
        'if failures:',
        '    raise RuntimeError(f"Could not load footprint(s): {failures}")',
        'b.Save("/workspace/kicad/missing_components.kicad_pcb")',
    ])
    gen_script_path = REPO / 'tools' / '_gen_missing_components.py'
    gen_script_path.write_text('\n'.join(script_lines))
    subprocess.run(
        ['docker', 'run', '--rm', '-v', f'{REPO}:/workspace', 'kicad/kicad:10.0.5',
         'python3', '/workspace/tools/_gen_missing_components.py'],
        check=True,
    )
    return placements


def apply():
    ensure_netlist()
    components, ref_pin_net = parse_netlist_xml(NETLIST_XML)
    board_text = PCB.read_text()

    fp_blocks = sexpr.find_footprint_blocks(board_text)
    existing_refs = set(fp_blocks.keys())
    netlist_refs = set(ref_pin_net.keys())
    missing_refs = sorted(netlist_refs - existing_refs)
    print(f'Existing: {len(existing_refs)}, netlist: {len(netlist_refs)}, missing: {missing_refs}')

    # Update existing pads
    updates = 0
    for ref in sorted(existing_refs & netlist_refs):
        start, end, block = fp_blocks[ref]
        new_block = block
        for pin, netname in ref_pin_net[ref].items():
            new_block = sexpr.set_pad_net(new_block, pin, netname)
        if new_block != block:
            board_text = board_text[:start] + new_block + board_text[end:]
            updates += 1
            fp_blocks = sexpr.find_footprint_blocks(board_text)

    print(f'Updated existing footprints: {updates}')

    # Generate missing
    if missing_refs:
        placements = generate_missing_footprints(missing_refs, components, ref_pin_net)
        missing_text = MISSING_PCB.read_text()
        missing_fp_blocks = sexpr.find_footprint_blocks(missing_text)
        not_inserted = [r for r in missing_refs if r not in missing_fp_blocks]
        if not_inserted:
            raise RuntimeError(f'Footprints could not be generated/loaded: {not_inserted}')
        for ref in missing_refs:
            start, end, block = missing_fp_blocks[ref]
            x, y = placements[ref]
            block = set_at_in_block(block, x, y)
            block = sexpr.set_property(block, 'Reference', ref)
            block = sexpr.set_property(block, 'Value', components[ref]['value'])
            for pin, netname in ref_pin_net.get(ref, {}).items():
                block = sexpr.set_pad_net(block, pin, netname)
            # Insert in the footprint section, before the first drawing/track/zone.
            marker = re.search(r'\n\t\((?:gr_|zone\s|segment\s|via\s|dimension\s|group\s|target\s)', board_text)
            if marker:
                board_text = board_text[:marker.start()] + '\n' + block + marker.group(0) + board_text[marker.end():]
            else:
                # fallback: append before final closing paren
                marker = re.search(r'\n\t\(embedded_fonts no\)\n\)\s*$', board_text)
                if marker:
                    board_text = board_text[:marker.start()] + '\n' + block + marker.group(0)
                else:
                    board_text = board_text.rstrip() + '\n' + block + '\n)'
            print(f'Inserted {ref} at ({x}, {y})')

    OUT.write_text(board_text)
    print(f'Wrote {OUT}')


if __name__ == '__main__':
    apply()
