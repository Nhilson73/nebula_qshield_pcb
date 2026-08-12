#!/usr/bin/env python3
import re, collections
with open('/workspace/kicad/nebula_qshield-drc.rpt') as f:
    text=f.read()
blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    for line in block.split('\n'):
        m=re.match(r'\s+@\(([\-\d\.]+) mm, ([\-\d\.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) \[([^\]]+)\](?: of ([^\n]+?))?(?: on ([\w\. \-]+))?', line)
        if m:
            layer=m.group(6).strip() if m.group(6) else 'F.Cu - B.Cu'
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer_raw':layer})
    if len(items)==2:
        pairs.append(items)
print('total', len(pairs))
by_net=collections.defaultdict(int)
for p in pairs:
    by_net[p[0]['net']]+=1
for net,c in sorted(by_net.items(), key=lambda x:-x[1]):
    print(net, c)
print('\nSample pairs:')
for p in pairs[:30]:
    print(p[0]['net'], p[0]['type'], p[0].get('ref',''), p[0]['layer_raw'], '<->', p[1]['type'], p[1].get('ref',''), p[1]['layer_raw'])
