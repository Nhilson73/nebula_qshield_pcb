import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/workspace/kicad/nebula_qshield.kicad_pcb')
text = path.read_text()

# Find the gr_poly block with the power-button uuid and remove it
marker = '(uuid "6a97222f-a69d-4a5f-87f0-9826f6a3cf0c")'
idx = text.find(marker)
if idx == -1:
    print('uuid not found')
    sys.exit(1)

# Search backwards for the opening (gr_poly
start = text.rfind('(gr_poly', 0, idx)
if start == -1:
    print('opening not found')
    sys.exit(1)

# Search forwards for the closing ) after uuid line
end = text.find(')', idx)
if end == -1:
    print('closing not found')
    sys.exit(1)

# include newline after closing paren
end = text.find('\n', end) + 1
print(f'Removing from {start} to {end}')
new_text = text[:start] + text[end:]
path.write_text(new_text)
print('Done')
