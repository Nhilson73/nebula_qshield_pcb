import re
text=open('/workspace/kicad/nebula_qshield-drc.rpt').read()
blocks=re.split(r'(?=\[unconnected_items\]: Missing connection between items)', text)
for block in blocks[1:]:
    if '/12V_RAIL' in block:
        print('---')
        for line in block.split('\n'):
            if '@(' in line: print(line.strip())
