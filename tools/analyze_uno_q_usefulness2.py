import re, math, pcbnew
b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')
MM=1e6
fp=b.FindFootprintByReference('J21')
ox=fp.GetPosition().x/MM; oy=fp.GetPosition().y/MM
ex=ox+68.58; ey=oy+53.34
def in_env(x,y):
    return ox<=x<=ex and oy<=y<=ey
def dist_env(x,y):
    dx=max(ox-x,0,x-ex); dy=max(oy-y,0,y-ey); return math.hypot(dx,dy)
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
# show all pairs with env status
d=open('/workspace/tools/uno_q_analysis.txt','w')
for i,(a,b) in enumerate(pairs,1):
    d.write(f"{i}. {a['net']}\n")
    d.write(f"   A: ({a['x']},{a['y']}) type={a['type']} ref={a['ref']} layer={a['layer']} in_env={in_env(a['x'],a['y'])} dist={dist_env(a['x'],a['y']):.2f}\n")
    d.write(f"   B: ({b['x']},{b['y']}) type={b['type']} ref={b['ref']} layer={b['layer']} in_env={in_env(b['x'],b['y'])} dist={dist_env(b['x'],b['y']):.2f}\n")
d.close()
print('written /workspace/tools/uno_q_analysis.txt')
