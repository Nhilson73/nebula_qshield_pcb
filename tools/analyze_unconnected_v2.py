#!/usr/bin/env python3
import re, collections
with open('/workspace/kicad/nebula_qshield-drc.rpt') as f:
    text=f.read()
blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    for line in block.split('\n'):
        m=re.match(r'\s+@\(([\-\d\.]+) mm, ([\-\d\.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) \[([^\]]+)\](?: of ([^ ]+))?(?: on ([\w\. \-]+))?', line)
        if m:
            layer=m.group(6).strip() if m.group(6) else ('F.Cu - B.Cu' if 'PTH' in m.group(3) else 'F.Cu')
            if 'PTH' in m.group(3): layer='F.Cu - B.Cu'
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer':layer})
    if len(items)==2:
        pairs.append(items)

by_net=collections.defaultdict(list)
for p in pairs:
    by_net[p[0]['net']].append(p)

md=[]
md.append('# Análisis de nets desconectadas')
md.append(f'**Total pares:** {len(pairs)}')
md.append('')
md.append('## Resumen por red')
md.append('| Net | Pares |')
md.append('| --- | --- |')
for net,c in sorted(by_net.items(), key=lambda x:-len(x[1])):
    md.append(f'| {net} | {len(c)} |')

md.append('')
md.append('## Detalle de pares (Net, Tipo_A, Ref_A, Capa_A, x_A, y_A -> Tipo_B, Ref_B, Capa_B, x_B, y_B)')
md.append('| Net | A | Ref A | Capa A | xA | yA | B | Ref B | Capa B | xB | yB |')
md.append('| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |')
for p in pairs:
    a,b=p
    md.append(f"| {a['net']} | {a['type']} | {a['ref']} | {a['layer']} | {a['x']} | {a['y']} | {b['type']} | {b['ref']} | {b['layer']} | {b['x']} | {b['y']} |")

with open('/workspace/tools/unconnected_report.md','w') as f:
    f.write('\n'.join(md))
print('wrote unconnected_report.md')
