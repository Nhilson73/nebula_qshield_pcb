import json, re
from pathlib import Path

MAPPING = json.loads(Path('kicad/tier_dnp_mapping.json').read_text())

_RE_PROP_VALUE = re.compile(
    r'\(\s*property\s+"([^"]+)"\s+"([^"]*)"',
    re.DOTALL
)

_RE_SYMBOL_START = re.compile(r'^\s*\(\s*symbol\b', re.DOTALL)
_RE_LIB_ID = re.compile(r'\(\s*lib_id\b')
_RE_IN_BOM_YES = re.compile(r'\(\s*in_bom\s+yes\s*\)')
_RE_DNP_PROP = re.compile(r'\(\s*property\s+"DNP"', re.DOTALL)
_RE_REF_PROP = re.compile(r'\(\s*property\s+"Reference"', re.DOTALL)


def get_outer_kicad_sch(text):
    """Return (body_start, body_end, body_text) for the outer (kicad_sch ... ) body."""
    start = text.find('(')
    if start != 0:
        return None
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


def get_property(block, name):
    """Return the string value of the named property, or None."""
    pattern = re.compile(
        r'\(\s*property\s+"' + re.escape(name) + r'"\s+"([^"]*)"',
        re.DOTALL
    )
    m = pattern.search(block)
    return m.group(1) if m else None


def find_balanced_end(text, start):
    """Return index just after the matching close paren for an open paren at start."""
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
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
                return i + 1
    return None


def ref_of(block):
    return get_property(block, 'Reference')


def is_instance(block):
    if not _RE_SYMBOL_START.search(block):
        return False
    if not _RE_LIB_ID.search(block):
        return False
    if not _RE_IN_BOM_YES.search(block):
        return False
    return True


def update_block(block, dnp):
    # If DNP exists, replace value (preserve surrounding whitespace/format)
    if _RE_DNP_PROP.search(block):
        return re.sub(
            r'(\(\s*property\s+"DNP"\s+)"[^"]*"',
            rf'\1"{dnp}"',
            block,
            count=1
        )
    # Find Reference property and insert a compact DNP property right after it
    m = _RE_REF_PROP.search(block)
    if not m:
        return block
    ref_end = find_balanced_end(block, m.start())
    if ref_end is None:
        return block
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
    new_body = body
    changed = False
    # process from end to start to preserve positions
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
