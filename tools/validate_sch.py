from pathlib import Path
import sys

def check(path):
    text = Path(path).read_text()
    balance = 0
    in_string = False
    escape = False
    for i, c in enumerate(text):
        if in_string:
            if escape:
                escape = False
                continue
            if c == '\\':
                escape = True
                continue
            if c == '"':
                in_string = False
                continue
        else:
            if c == '"':
                in_string = True
                continue
            if c == '(':
                balance += 1
            elif c == ')':
                balance -= 1
                if balance < 0:
                    print(f'Unbalanced ) at {i} in {path}')
                    return False
    if balance != 0:
        print(f'Unbalanced parentheses (balance {balance}) in {path}')
        return False
    print(f'{path}: OK')
    return True

ok = True
for p in Path('kicad').glob('*.kicad_sch'):
    ok &= check(p)
sys.exit(0 if ok else 1)
