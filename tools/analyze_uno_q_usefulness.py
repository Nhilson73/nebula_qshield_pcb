import re, math, pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
# UNO Q envelope: J21 origin + 68.58 x 53.34
fp=b.FindFootprintByReference('J21')
ox=fp.GetPosition().x/MM; oy=fp.GetPosition().y/MM
ex=ox+68.58; ey=oy+53.34
def in_env(x,y):
    return ox<=x<=ex and oy<=y<=ey
# parse DRC unconnected pairs
text=open('/workspace/kicad/nebula_qshield-drc.rpt').read()
blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
pairs=[]
for block in blocks[1:]:
    items=[]
    for line in block.split('\n'):
        m=re.match(r'\s+@\(([\-\d\.]+) mm, ([\-\d\.]+) mm\): (Pad \d+|PTH pad \d+|Track|Via|Zone) \[([^\]]+)\](?: of ([^ ]+))?(?: on ([\w\. \-]+))?', line)
        if m:
            items.append({'x':float(m.group(1)),'y':float(m.group(2)),'type':m.group(3),'net':m.group(4),'ref':m.group(5),'layer':m.group(6)})
    if len(items)==2:
        pairs.append((items[0],items[1]))
print('total pairs', len(pairs))
print('UNO Q envelope x', ox, ex, 'y', oy, ey)
# classify by net
from collections import Counter
cnt=Counter([p[0]['net'] for p in pairs])
for n,c in cnt.most_common(): print(n,c)
# endpoints inside UNO Q envelope
inside=0; near=0
for a,b in pairs:
    if in_env(a['x'],a['y']) or in_env(b['x'],b['y']): inside+=1
    # distance from envelope < 10 mm
    def dist_env(x,y):
        dx=max(ox-x,0,x-ex); dy=max(oy-y,0,y-ey); return math.hypot(dx,dy)
    if dist_env(a['x'],a['y'])<10 or dist_env(b['x'],b['y'])<10: near+=1
print('endpoints inside UNO Q envelope:', inside)
print('endpoints within 10 mm of UNO Q envelope:', near)
# show some pairs and their envelope proximity
for a,b in pairs[:20]:
    print(a['net'])
    print(' ', a['x'],a['y'], 'in_env', in_env(a['x'],a['y']))
    print(' ', b['x'],b['y'], 'in_env', in_env(b['x'],b['y']))
