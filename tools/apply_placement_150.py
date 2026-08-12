import json, pcbnew

with open('/workspace/kicad/resolved_scipy_150.json') as f:
    pos=json.load(f)

b=pcbnew.LoadBoard('/workspace/kicad/nebula_qshield.kicad_pcb')

for ref, (x,y) in pos.items():
    fp=b.FindFootprintByReference(ref)
    if fp is None:
        print('not found', ref); continue
    fp.SetPosition(pcbnew.VECTOR2I(int(round(x*1e6)), int(round(y*1e6))))

# Delete all tracks and vias
for item in list(b.GetTracks()):
    b.Remove(item)

pcbnew.SaveBoard('/workspace/kicad/nebula_qshield.kicad_pcb', b)
print('Applied 150x120 placement, removed tracks, saved board.')
