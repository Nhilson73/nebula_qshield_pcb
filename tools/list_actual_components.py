import re, glob, json
from pathlib import Path

def parse_sexpr_blocks(text, keyword):
    stack = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '(':
            m = re.match(r'(' + re.escape(keyword) + r')\b', text[i+1:])
            if m and (not stack or stack[-1][0] is None):
                stack.append((keyword, i))
            else:
                stack.append((None, i))
        elif c == ')':
            if stack:
                kw, s = stack.pop()
                if kw == keyword:
                    yield text[s:i+1]
        elif c == '"':
            j = text.find('"', i+1)
            if j == -1:
                break
            i = j
        i += 1

props = ['Reference','Value','Footprint','Description']
all_items = []
for path in sorted(glob.glob('kicad/*.kicad_sch')):
    text = Path(path).read_text()
    for block in parse_sexpr_blocks(text, 'symbol'):
        if '(in_bom yes)' not in block or '(lib_id' not in block:
            continue
        item = {'sheet': Path(path).name}
        for prop in props:
            m = re.search(r'\(property "' + prop + r'" "([^"]*)"', block)
            item[prop] = m.group(1) if m else ''
        dnp = re.search(r'\(property "DNP" "([^"]*)"', block)
        item['DNP'] = dnp.group(1) if dnp else ''
        if item.get('Reference') and not item['Reference'].startswith('#'):
            all_items.append(item)

Path('kicad/actual_components.json').write_text(json.dumps(all_items, indent=2))
print('total', len(all_items))
print(json.dumps({k: len([x for x in all_items if x['sheet']==k]) for k in sorted({x['sheet'] for x in all_items})}))
