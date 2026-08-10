"""Minimal S-expression parser with string handling for KiCad .kicad_pcb files."""
import re
from typing import List, Tuple


def split_top_level(text: str) -> List[Tuple[int, int, str]]:
    """Return a list of (start, end, block) for each top-level s-expression."""
    items = []
    i = 0
    depth = 0
    start = None
    in_string = False
    escape = False
    while i < len(text):
        c = text[i]
        if in_string:
            if escape:
                escape = False
            elif c == '\\':
                escape = True
            elif c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c == '(':
            if depth == 0:
                start = i
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0 and start is not None:
                items.append((start, i + 1, text[start:i + 1]))
                start = None
        i += 1
    return items


def find_subblocks(block: str, symbol: str) -> List[Tuple[int, int, str]]:
    """Find all balanced sub-blocks starting with (symbol ...)."""
    pattern = re.compile(r'\(\s*' + re.escape(symbol) + r'(\s|\))')
    blocks = []
    for m in pattern.finditer(block):
        start = m.start()
        i = start
        depth = 0
        in_string = False
        escape = False
        while i < len(block):
            c = block[i]
            if in_string:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_string = False
                i += 1
                continue
            if c == '"':
                in_string = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    blocks.append((start, i + 1, block[start:i + 1]))
                    break
            i += 1
    return blocks


def _unquote(token: str) -> str:
    if token.startswith('"') and token.endswith('"'):
        return token[1:-1].replace('\\"', '"').replace('\\\\', '\\')
    return token


def _quote(token: str) -> str:
    escaped = token.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def get_property(block: str, name: str) -> str:
    for start, end, sub in find_subblocks(block, 'property'):
        parts = tokenize_sexpr(sub)
        if len(parts) >= 3 and _unquote(parts[1]) == name:
            return _unquote(parts[2])
    return None


def set_property(block: str, name: str, value: str) -> str:
    for start, end, sub in find_subblocks(block, 'property'):
        parts = tokenize_sexpr(sub)
        if len(parts) >= 3 and _unquote(parts[1]) == name:
            # replace the value token (position 2) preserving quotes
            old = extract_token(sub, 2)
            new = _quote(value)
            sub_new = sub[:old[0]] + new + sub[old[1]:]
            block = block[:start] + sub_new + block[end:]
            return block
    return block


def tokenize_sexpr(block: str):
    """Very rough tokenizer: returns string tokens, handling quoted strings."""
    tokens = []
    i = 0
    in_string = False
    token = ''
    while i < len(block):
        c = block[i]
        if in_string:
            token += c
            if c == '"':
                if len(token) > 1 and token[-2] != '\\':
                    in_string = False
                    tokens.append(token)
                    token = ''
        else:
            if c == '"':
                if token:
                    tokens.append(token.strip())
                    token = ''
                in_string = True
                token = '"'
            elif c in '() \t\n':
                if token.strip():
                    tokens.append(token.strip())
                    token = ''
            else:
                token += c
        i += 1
    if token.strip():
        tokens.append(token.strip())
    return tokens


def extract_token(block: str, token_index: int) -> Tuple[int, int, str]:
    """Return (start, end, text) of the n-th token in an s-expression string."""
    count = 0
    i = 0
    in_string = False
    token_start = None
    token_buf = ''
    while i < len(block):
        c = block[i]
        if in_string:
            token_buf += c
            if c == '"':
                if token_buf[-2] != '\\':
                    in_string = False
                    if count == token_index:
                        return token_start, i + 1, token_buf
                    count += 1
                    token_buf = ''
        else:
            if c == '"':
                token_start = i
                in_string = True
                token_buf = '"'
            elif not c.isspace() and c not in '()':
                token_start = i
                while i < len(block) and not block[i].isspace() and block[i] not in '()':
                    i += 1
                if count == token_index:
                    return token_start, i, block[token_start:i]
                count += 1
                continue
        i += 1
    return None


def quote_value(value: str) -> str:
    """Return a KiCad-safe quoted string if needed."""
    if value and re.match(r'^[A-Za-z0-9_.\-/]+$', value):
        return f'"{value}"'
    # escape quotes
    escaped = value.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'


def set_pad_net(footprint_text: str, pin: str, new_net: str) -> str:
    """Update or add the (net ...) attribute inside a pad sub-block."""
    pad_pattern = re.compile(r'\(pad\s+"?' + re.escape(pin) + r'"?(\s|\))')
    for m in pad_pattern.finditer(footprint_text):
        start = m.start()
        # find end of this pad block
        i = start
        depth = 0
        in_string = False
        escape = False
        pad_end = None
        while i < len(footprint_text):
            c = footprint_text[i]
            if in_string:
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_string = False
                i += 1
                continue
            if c == '"':
                in_string = True
            elif c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    pad_end = i + 1
                    break
            i += 1
        if pad_end is None:
            continue
        pad_block = footprint_text[start:pad_end]
        # check if this pad block belongs to this footprint (not a nested fp_text etc)
        if not pad_block.startswith('(pad'):
            continue
        # find net line
        net_m = re.search(r'\(net\s+"([^"]*)"\)', pad_block)
        if net_m:
            old = net_m.group(0)
            new = f'(net {quote_value(new_net)})'
            pad_block_new = pad_block.replace(old, new, 1)
        else:
            # insert (net ...) before the closing paren
            new = f'\n\t\t\t(net {quote_value(new_net)})'
            # find the last ) and insert before it
            pad_block_new = pad_block[:-1] + new + '\n\t\t)'
        footprint_text = footprint_text[:start] + pad_block_new + footprint_text[pad_end:]
        return footprint_text
    return footprint_text


def find_footprint_blocks(text: str) -> dict:
    """Return dict ref -> (start, end, block) for top-level footprint blocks."""
    blocks = {}
    for start, end, block in find_subblocks(text, 'footprint'):
        # only top-level footprint blocks (not nested inside 3d model or other)
        # heuristic: block starts near column 1 (preceded by tab or newline)
        ref = get_property(block, 'Reference')
        if ref:
            blocks[ref] = (start, end, block)
    return blocks
