import re, collections
text=open('/workspace/kicad/nebula_qshield-drc.rpt').read()
blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    net=None
    for line in block.split('\n'):
        m=re.match(r'\s+@\(([\-\d\.]+) mm, ([\-\d\.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) \[([^\]]+)\](?: of ([^ ]+))?(?: on ([\w\. \-]+))?', line)
        if m:
            layer=m.group(6).strip() if m.group(6) else ('F.Cu - B.Cu' if 'PTH' in m.group(3) else 'F.Cu')
            if 'PTH' in m.group(3): layer='F.Cu - B.Cu'
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer':layer})
            if net is None: net=m.group(4)
    if len(items)==2:
        pairs.append((net, items))
counts=collections.Counter([n for n,_ in pairs])
print('total pairs', len(pairs))
for n,c in counts.most_common(20):
    print(n, c)
print('\n12V_RAIL pairs:')
for n,its in pairs:
    if '/12V_RAIL' in n:
        print(n)
        for i in its: print(' ', i)
