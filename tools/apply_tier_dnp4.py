import json, re
from pathlib import Path

MAPPING = json.loads(Path('kicad/tier_dnp_mapping.json').read_text())

def get_outer_kicad_sch(text):
    """Return (body_start, body_end, body_text) for the outer (kicad_sch ... ) body."""
    # find first '('
    start = text.find('(')
    if start != 0:
        return None
    # parse to matching ')' at top level
    depth = 0
    in_string = False
    escape = False
    end = None
    for i, c in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
        elif c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end is None:
        return None
    # body is between outer ( and )
    return 1, end, text[1:end]

def top_level_blocks(body):
    """Yield (start, end, block) for each top-level s-expression in body."""
    i = 0
    n = len(body)
    while i < n:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        if body[i] != '(':
            # skip non-parenthesis token (e.g. kicad_sch)
            while i < n and not body[i].isspace() and body[i] not in '()':
                i += 1
            continue
        start = i
        depth = 0
        in_string = False
        escape = False
        while i < n:
            c = body[i]
            if in_string:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_string = False
            else:
                if c == '"':
                    in_string = True
                elif c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        i += 1
                        yield start, i, body[start:i]
                        break
            i += 1

def ref_of(block):
    m = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', block)
    return m.group(1) if m else None

def is_instance(block):
    return (
        block.lstrip().startswith('(symbol') and
        '(lib_id' in block and
        '(in_bom yes)' in block
    )

def update_block(block, dnp):
    # If DNP exists, replace value
    if re.search(r'\(property\s+"DNP"', block):
        return re.sub(r'(\(property\s+"DNP"\s+)"[^"]*"', rf'\1"{dnp}"', block)
    # Find Reference property end
    m = re.search(r'\(property\s+"Reference"', block)
    if not m:
        return block
    # parse balanced from m.start()
    pos = m.start()
    depth = 0
    in_string = False
    escape = False
    ref_end = None
    for i in range(pos, len(block)):
        c = block[i]
        if in_string:
            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == '"':
                in_string = False
        else:
            if c == '"':
                in_string = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    ref_end = i + 1
                    break
    if ref_end is None:
        return block
    # indentation from line start
    line_start = block.rfind('\n', 0, m.start()) + 1
    indent = block[line_start:m.start()]
    dnp_prop = f'\n{indent}(property "DNP" "{dnp}" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
    return block[:ref_end] + dnp_prop + block[ref_end:]

def process_file(path):
    text = path.read_text()
    outer = get_outer_kicad_sch(text)
    if not outer:
        return False
    body_start, body_end, body = outer
    children = list(top_level_blocks(body))
    if not children:
        return False
    changed = False
    new_body = body
    # process children from end to start to preserve positions
    for start, end, block in reversed(children):
        if not is_instance(block):
            continue
        ref = ref_of(block)
        if not ref or ref.startswith('#'):
            continue
        dnp = MAPPING.get(ref)
        if dnp is None:
            continue
        block_new = update_block(block, dnp)
        if block_new == block:
            continue
        new_body = new_body[:start] + block_new + new_body[end:]
        changed = True
    if changed:
        new_text = '(' + new_body + ')'
        path.write_text(new_text)
        return True
    return False

if __name__ == '__main__':
    for path in sorted(Path('kicad').glob('*.kicad_sch')):
        if process_file(path):
            print(f'Updated {path}')
    print('Done')
