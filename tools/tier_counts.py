import json
m = json.loads(open('kicad/tier_dnp_mapping.json').read())

def populated(dnp, tier):
    if dnp in ('All',''):
        return dnp != 'All'
    if dnp == 'NO':
        return True
    if dnp == 'Optional':
        return False
    tiers = dnp.split(',')
    return tier not in tiers

for tier in ['Essential','Insight','Signature']:
    c = [r for r,d in m.items() if populated(d, tier)]
    print(f'{tier}: {len(c)}')

# show all by category
from collections import Counter
print('DNP values:', Counter(m.values()))
