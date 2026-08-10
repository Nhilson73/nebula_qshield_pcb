#!/usr/bin/env python3
"""
Correct the Arduino_UNO_Q_Shield footprint digital header pad numbering.

The original footprint had the 18-pin digital header row (pins 15-32)
numbered left-to-right, which is the reverse of the UNO R3/Q convention:
leftmost pin must be D21/SCL (pin 32) and rightmost pin D0 (pin 15).

This script swaps pad numbers 15<->32, 16<->31, ... 23<->24 and ensures
pin 15 keeps a rectangular keying pad while all other digital pins are oval.
"""
from pathlib import Path
import re

FOOTPRINT = Path(__file__).parent.parent / "kicad/lib/nebula_footprints.pretty/Arduino_UNO_Q_Shield.kicad_mod"


def mirror_pin(n: int) -> int:
    """Map a current digital-header pin (15..32) to its correct UNO R3/Q number."""
    if 15 <= n <= 32:
        return 47 - n
    return n


def main():
    text = FOOTPRINT.read_text()
    new_lines = []
    for line in text.splitlines():
        m = re.search(r'pad "(\d+)" thru_hole (rect|oval)', line)
        if m:
            n = int(m.group(1))
            old_shape = m.group(2)
            if 15 <= n <= 32:
                new_n = mirror_pin(n)
                # The rightmost pin (D0, pin 15) keeps a rectangular keying pad.
                new_shape = "rect" if new_n == 15 else "oval"
                line = line.replace(f'pad "{n}" thru_hole {old_shape}',
                                    f'pad "{new_n}" thru_hole {new_shape}')
        new_lines.append(line)
    FOOTPRINT.write_text("\n".join(new_lines) + "\n")
    print(f"Updated {FOOTPRINT}")


if __name__ == "__main__":
    main()
