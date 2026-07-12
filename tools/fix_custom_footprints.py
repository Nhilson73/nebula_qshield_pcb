#!/usr/bin/env python3
"""Add missing tstamp/uuid fields to custom KiCad 9 footprints.

KiCad 9 (pcbnew) refuses to load footprints whose pads, properties and
graphical items do not carry a tstamp. The original Devin-generated
nebula_footprints lack these, so this script parses the .kicad_mod files,
adds tstamp fields, and rewrites them in a KiCad-compatible format.
"""
import pathlib
import re
import uuid

ROOT = pathlib.Path(__file__).parent.parent / "kicad/lib/nebula_footprints.pretty"

# Element types that KiCad expects (or tolerates) with a tstamp field.
STAMP_TYPES = {
    "pad",
    "property",
    "fp_rect",
    "fp_circle",
    "fp_line",
    "fp_text",
    "fp_arc",
    "fp_poly",
    "fp_curve",
    "model",
}


def tokenize(text):
    """Very small S-expression tokenizer for KiCad .kicad_mod files."""
    text = re.sub(r";[^\n]*", "", text)
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c == "(" or c == ")":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 1
            tokens.append(("str", text[i + 1 : j]))
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            tok = text[i:j]
            if tok:
                tokens.append(("sym", tok))
            i = j
    return tokens


def parse(tokens):
    """Recursive descent parser from token list."""
    if not tokens:
        raise ValueError("empty token stream")
    t = tokens.pop(0)
    if t == "(":
        node = []
        while tokens[0] != ")":
            node.append(parse(tokens))
        tokens.pop(0)
        return node
    if t == ")":
        raise ValueError("unexpected ')'")
    return t


def add_tstamp(node):
    """Recursively add tstamp to supported elements."""
    if not isinstance(node, list):
        return
    if node and isinstance(node[0], tuple) and node[0][0] == "sym" and node[0][1] in STAMP_TYPES:
        has_tstamp = any(
            isinstance(x, list)
            and x
            and isinstance(x[0], tuple)
            and x[0][0] == "sym"
            and x[0][1] == "tstamp"
            for x in node
        )
        if not has_tstamp:
            node.append([("sym", "tstamp"), ("sym", str(uuid.uuid4()))])
    for child in node:
        add_tstamp(child)


def print_node(node, indent=0):
    """Pretty printer matching canonical KiCad .kicad_mod layout."""
    if isinstance(node, tuple):
        typ, val = node
        if typ == "str":
            return f'"{val}"'
        return val
    if isinstance(node, list):
        parts = [print_node(c, indent + 1) for c in node]
        has_sublist = any(isinstance(c, list) for c in node)
        if not has_sublist:
            return "(" + " ".join(parts) + ")"
        head = parts[0]
        lines = ["(" + head]
        for p in parts[1:]:
            lines.append("  " * (indent + 1) + p)
        lines.append("  " * indent + ")")
        return "\n".join(lines)
    return str(node)


def main():
    for fp in sorted(ROOT.glob("*.kicad_mod")):
        text = fp.read_text()
        tokens = tokenize(text)
        ast = parse(tokens)
        add_tstamp(ast)
        out = print_node(ast)
        fp.write_text(out + "\n")
        print(f"fixed {fp}")


if __name__ == "__main__":
    main()
