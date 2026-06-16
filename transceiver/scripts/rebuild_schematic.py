#!/usr/bin/env python3
"""
Rebuild PSN_TRX.kicad_sch from the clean pre-holes baseline,
then correctly add H1-H4 mounting holes inside lib_symbols.
"""

import re
import shutil
import uuid
from pathlib import Path

SCH       = Path('PSN_TRX.kicad_sch')
BASELINE  = Path('/tmp/pre_holes.kicad_sch')
MECH_LIB  = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Mechanical.kicad_sym')
ROOT_UUID = '50835569-93ad-4c8c-aafc-424a6a3761ef'
FP        = 'MountingHole:MountingHole_3.2mm_M3'


def uid():
    return str(uuid.uuid4())


def extract_symbol(lib_text: str, base_name: str) -> str:
    """Extract a complete (symbol "base_name" ...) block."""
    start = lib_text.find(f'(symbol "{base_name}"')
    if start == -1:
        raise ValueError(f'{base_name} not found')
    depth = 0
    for i in range(start, len(lib_text)):
        if lib_text[i] == '(':
            depth += 1
        elif lib_text[i] == ')':
            depth -= 1
            if depth == 0:
                return lib_text[start:i + 1]
    raise ValueError('unclosed symbol')


def find_lib_symbols_end(content: str) -> int:
    """Return index of closing ) of (lib_symbols ...)."""
    start = content.find('\n\t(lib_symbols\n')
    depth = 0
    for i in range(start + 1, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError('lib_symbols not closed')


EFFECTS = '''\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)'''


def make_hole(ref: str, x: float, y: float) -> str:
    return f'''
\t(symbol
\t\t(lib_id "Mechanical:MountingHole")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom no)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y - 3.81} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Value" "MountingHole"
\t\t\t(at {x} {y - 5.715} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Footprint" "{FP}"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(instances
\t\t\t(project "PSN_TRX"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def main():
    shutil.copy(SCH, SCH.with_suffix('.kicad_sch.broken_bak'))
    content = BASELINE.read_text(encoding='utf-8')

    # 1. Build lib entry for Mechanical:MountingHole
    mech_lib = MECH_LIB.read_text(encoding='utf-8')
    mh_raw = extract_symbol(mech_lib, 'MountingHole')
    # Prefix names with "Mechanical:"
    mh_entry = re.sub(
        r'\(symbol "MountingHole((?:_\w+)*)"',
        r'(symbol "Mechanical:MountingHole\1"',
        mh_raw,
    )
    # Indent to two tabs (inside lib_symbols block)
    mh_entry = '\t\t' + mh_entry.replace('\n', '\n\t\t').rstrip('\t')

    # 2. Insert into lib_symbols
    ls_end = find_lib_symbols_end(content)
    content = content[:ls_end] + '\n' + mh_entry + '\n\t' + content[ls_end:]
    print('lib_symbols: added Mechanical:MountingHole')

    # 3. Add H1-H4 before final closing paren
    holes = [
        ('H1', 760.0, 30.0),
        ('H2', 780.0, 30.0),
        ('H3', 760.0, 50.0),
        ('H4', 780.0, 50.0),
    ]
    blocks = ''.join(make_hole(r, x, y) for r, x, y in holes)
    insert = content.rfind('\n)')
    content = content[:insert] + blocks + content[insert:]
    print('Added H1, H2, H3, H4 symbols')

    SCH.write_text(content, encoding='utf-8')
    print(f'Saved: {SCH}')


if __name__ == '__main__':
    main()
