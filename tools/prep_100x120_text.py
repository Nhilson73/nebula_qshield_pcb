#!/usr/bin/env python3
"""Prepare the 100x120 mm board file from the current re-arch board.

- Copies nebula_qshield.kicad_pcb -> nebula_qshield_100x120.kicad_pcb
- Replaces the board outline Edge.Cuts polygon with a 100x120 mm rounded rectangle.
- Removes all (segment) and (via) blocks (tracks/vias) to provide a clean routing baseline.
- Keeps the UNO Q connector cutouts and Eco1.User keepout markers as-is.
"""

import re, math, shutil, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'kicad', 'nebula_qshield.kicad_pcb')
DST = os.path.join(ROOT, 'kicad', 'nebula_qshield_100x120.kicad_pcb')
BOARD_OUTLINE_UUID = '15d6e1d0-52dd-4f8d-bf98-d3c300d4c955'

def gen_board_outline_pts():
    W, H = 100.0, 120.0
    R = 2.5
    pts = []
    steps = 10
    def arc(cx, cy, r, a0, a1):
        # exclude the first endpoint to avoid duplicate points
        for i in range(1, steps + 1):
            a = math.radians(a0 + (a1 - a0) * i / steps)
            pts.append((round(cx + r * math.cos(a), 6), round(cy + r * math.sin(a), 6)))
    pts.append((0, R));       arc(R,     R,     R, 180, 270)
    pts.append((W - R, 0));   arc(W - R, R,     R, 270, 360)
    pts.append((W, H - R));   arc(W - R, H - R, R, 0,   90)
    pts.append((R, H));       arc(R,     H - R, R, 90,  180)
    pts.append((0, R))
    # format similar to KiCad output: groups of 5 per line
    lines = []
    line = '\t\t\t'
    for i, (x, y) in enumerate(pts):
        line += f'(xy {x} {y}) '
        if (i + 1) % 5 == 0:
            lines.append(line.rstrip())
            line = '\t\t\t'
    if line.strip():
        lines.append(line.rstrip())
    return '\n'.join(lines)

def collect_block(lines, start):
    """Collect a top-level s-expression starting at lines[start]. Return (block_lines, end_index)."""
    block = [lines[start]]
    depth = lines[start].count('(') - lines[start].count(')')
    i = start + 1
    while depth > 0 and i < len(lines):
        block.append(lines[i])
        depth += lines[i].count('(') - lines[i].count(')')
        i += 1
    return block, i

def adjust_cutout_pts(block):
    """Fix cutout coordinates that overlap the J21 header pads."""
    block_str = ''.join(block)
    # USB-C cutout: narrow right edge to avoid J21 pin 15
    if '89d7af95-7009-4ff0-87a6-60480c4eb85b' in block_str:
        new_block = []
        for line in block:
            new_line = re.sub(r'\(xy 23\.08 ', '(xy 22.5 ', line)
            new_block.append(new_line)
        return new_block
    # Power jack cutout: raise bottom edge to avoid J21 pins 29-32
    if '8ae0881b-d64c-4b10-914d-9b4b62d94bca' in block_str:
        new_block = []
        for line in block:
            new_line = re.sub(r'\(xy (\d+\.\d+) 85\.56\)', r'(xy \1 88.56)', line)
            new_block.append(new_line)
        return new_block
    return block

def process(src, dst):
    with open(src, 'r') as f:
        lines = f.readlines()

    out_lines = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r'^\t\(([a-zA-Z0-9_]+)', line)
        if not m:
            out_lines.append(line)
            i += 1
            continue
        name = m.group(1)
        if name in ('segment', 'via'):
            block, i = collect_block(lines, i)
            continue
        if name == 'gr_poly':
            block, next_i = collect_block(lines, i)
            if f'(uuid "{BOARD_OUTLINE_UUID}")' in ''.join(block):
                # replace with new rounded rectangle outline
                out_lines.append('\t(gr_poly\n')
                out_lines.append('\t\t(pts\n')
                out_lines.append(gen_board_outline_pts() + '\n')
                out_lines.append('\t\t)\n')
                out_lines.append('\t\t(stroke\n')
                out_lines.append('\t\t\t(width 0.1)\n')
                out_lines.append('\t\t\t(type default)\n')
                out_lines.append('\t\t)\n')
                out_lines.append('\t\t(fill no)\n')
                out_lines.append('\t\t(layer "Edge.Cuts")\n')
                out_lines.append(f'\t\t(uuid "{BOARD_OUTLINE_UUID}")\n')
                out_lines.append('\t)\n')
                i = next_i
                continue
            else:
                # keep cutout/keepout polygon, but adjust Edge.Cuts cutouts
                # that overlap the J21 header pads
                out_lines.extend(adjust_cutout_pts(block))
                i = next_i
                continue
        # default: copy line and move on
        out_lines.append(line)
        i += 1

    with open(dst, 'w') as f:
        f.writelines(out_lines)
    print('Wrote', dst)

if __name__ == '__main__':
    shutil.copy(SRC, DST)
    # Copy project and custom DRC rule files so the new board is self-contained
    for ext in ('.kicad_pro', '.kicad_prl', '.kicad_dru'):
        src_support = SRC.replace('.kicad_pcb', ext)
        dst_support = DST.replace('.kicad_pcb', ext)
        if os.path.exists(src_support):
            shutil.copy(src_support, dst_support)
    process(DST, DST)
