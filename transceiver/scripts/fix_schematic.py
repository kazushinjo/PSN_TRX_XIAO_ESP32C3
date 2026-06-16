#!/usr/bin/env python3
"""Fix PSN_TRX.kicad_sch: add missing lib_symbols entries for H1-H4 and J1."""

import re
import shutil
from pathlib import Path

SCH = Path('PSN_TRX.kicad_sch')
MECH_LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Mechanical.kicad_sym')


def extract_symbol(lib_text: str, name: str) -> str:
    """Extract a single (symbol "name" ...) block from a .kicad_sym file."""
    start = lib_text.find(f'(symbol "{name}"')
    if start == -1:
        raise ValueError(f'Symbol "{name}" not found in library')
    depth = 0
    for i in range(start, len(lib_text)):
        if lib_text[i] == '(':
            depth += 1
        elif lib_text[i] == ')':
            depth -= 1
            if depth == 0:
                return lib_text[start:i + 1]
    raise ValueError(f'Unclosed symbol "{name}"')


def find_lib_symbols_end(content: str) -> int:
    """Return the position of the closing ) of (lib_symbols ...)."""
    start = content.find('\n\t(lib_symbols\n')
    depth = 0
    for i in range(start + 1, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i  # position of closing )
    raise ValueError('lib_symbols not closed')


def main():
    shutil.copy(SCH, SCH.with_suffix('.kicad_sch.fix_bak'))

    content = SCH.read_text(encoding='utf-8')
    mech_lib = MECH_LIB.read_text(encoding='utf-8')

    # Build the MountingHole lib entry with "Mechanical:" prefix
    mh_raw = extract_symbol(mech_lib, 'MountingHole')
    # Replace symbol name and sub-symbol names to include library prefix
    mh_entry = re.sub(
        r'\(symbol "MountingHole((?:_\w+)*)"',
        r'(symbol "Mechanical:MountingHole\1"',
        mh_raw,
    )
    # Indent to 2 tabs (inside lib_symbols)
    mh_entry = '\t\t' + mh_entry.replace('\n', '\n\t\t').rstrip('\t')

    # Insert into lib_symbols if not already there
    if '"Mechanical:MountingHole"' not in content:
        end_pos = find_lib_symbols_end(content)
        content = content[:end_pos] + '\n' + mh_entry + '\n\t' + content[end_pos:]
        print('Added Mechanical:MountingHole to lib_symbols')
    else:
        print('Mechanical:MountingHole already in lib_symbols')

    SCH.write_text(content, encoding='utf-8')
    print('Schematic saved.')


if __name__ == '__main__':
    main()
