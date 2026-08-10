import re, glob, json
from pathlib import Path
from apply_tier_dnp4 import get_outer_kicad_sch, top_level_blocks, get_property


def is_symbol_instance(block):
    # top-level symbol with lib_id and in_bom yes
    if not re.search(r'^\s*\(\s*symbol\b', block, re.DOTALL):
        return False
    if not re.search(r'\(\s*lib_id\b', block):
        return False
    if not re.search(r'\(\s*in_bom\s+yes\s*\)', block):
        return False
    ref = get_property(block, 'Reference')
    return ref and not ref.startswith('#')


def main():
    all_items = []
    props = ['Reference', 'Value', 'Footprint', 'Description']
    for path in sorted(glob.glob('kicad/*.kicad_sch')):
        text = Path(path).read_text()
        outer = get_outer_kicad_sch(text)
        if not outer:
            continue
        _, _, body = outer
        for start, end, block in top_level_blocks(body):
            if not is_symbol_instance(block):
                continue
            item = {'sheet': Path(path).name}
            for prop in props:
                item[prop] = get_property(block, prop) or ''
            item['DNP'] = get_property(block, 'DNP') or ''
            all_items.append(item)

    Path('kicad/actual_components.json').write_text(json.dumps(all_items, indent=2))
    print('total', len(all_items))
    print(json.dumps({k: len([x for x in all_items if x['sheet'] == k]) for k in sorted({x['sheet'] for x in all_items})}))


if __name__ == '__main__':
    main()
