#!/usr/bin/env python3
"""
Update PSN_TRX.kicad_pcb from PSN_TRX.net using KiCad Python API.
Equivalent to KiCad's Tools > Update PCB from Schematic.

Run with KiCad's bundled Python:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 update_pcb_from_netlist.py
"""

import sys
import os
import re
from pathlib import Path

# Add KiCad Python API
KICAD_PY = '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages'
sys.path.insert(0, KICAD_PY)

import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
NET_FILE    = PROJECT_DIR / 'PSN_TRX.net'

# on_board no の部品（外付けVR）はPCBに配置しない
EXCLUDE_REFS = {'VR1', 'VR2'}

# KiCad footprint library search paths
FP_SEARCH_PATHS = [
    PROJECT_DIR / 'PSN_TRX.pretty',
    Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'),
    Path.home() / 'Library/Application Support/kicad/9.0/footprints',
    Path.home() / 'Library/Application Support/kicad/10.0/footprints',
]


def find_footprint(lib_ref: str):
    """Find the .kicad_mod file for a LibName:FootprintName reference."""
    if ':' not in lib_ref:
        return None
    lib_name, fp_name = lib_ref.split(':', 1)
    for base in FP_SEARCH_PATHS:
        candidate = base / f'{lib_name}.pretty' / f'{fp_name}.kicad_mod'
        if candidate.exists():
            return str(candidate)
        # Also check base directly for custom library
        candidate2 = base / f'{fp_name}.kicad_mod'
        if candidate2.exists():
            return str(candidate2)
    return None


def parse_netlist(net_file: Path) -> list[dict]:
    """Parse KiCad S-expression netlist, return list of component dicts."""
    content = net_file.read_text(encoding='utf-8')
    components = []

    for comp_m in re.finditer(
        r'\(comp\s+\(ref\s+"([^"]+)"\)'
        r'(?:(?!\(comp\s).)*?\(value\s+"([^"]+)"\)'
        r'(?:(?!\(comp\s).)*?\(footprint\s+"([^"]+)"\)',
        content, re.DOTALL
    ):
        ref, value, fp = comp_m.group(1), comp_m.group(2), comp_m.group(3)
        if fp:  # skip power symbols without footprints
            components.append({'ref': ref, 'value': value, 'footprint': fp})

    return components


def main():
    print(f'Loading PCB: {PCB_FILE}')
    board = pcbnew.LoadBoard(str(PCB_FILE))

    print(f'Parsing netlist: {NET_FILE}')
    components = parse_netlist(NET_FILE)
    print(f'  Found {len(components)} components with footprints')

    # Get existing references in the PCB
    existing_refs = {fp.GetReference() for fp in board.GetFootprints()}
    print(f'  Already in PCB: {len(existing_refs)} footprints')

    # Placement grid: stack new components to the right of the board
    # Board is 150x100mm; place newcomers starting at x=160, y=10
    place_x = pcbnew.FromMM(160)
    place_y = pcbnew.FromMM(10)
    col_step = pcbnew.FromMM(5)
    row_step = pcbnew.FromMM(5)
    col_count = 0
    max_cols = 20

    added = 0
    not_found = []

    for comp in components:
        ref = comp['ref']
        if ref in existing_refs or ref in EXCLUDE_REFS:
            continue  # already placed or excluded (on_board no)

        fp_path = find_footprint(comp['footprint'])
        if not fp_path:
            not_found.append(f"{ref} ({comp['footprint']})")
            continue

        # Load footprint from file
        fp = pcbnew.FootprintLoad(
            str(Path(fp_path).parent),
            Path(fp_path).stem
        )
        if fp is None:
            not_found.append(f"{ref} (load failed)")
            continue

        # Set reference and value
        fp.SetReference(ref)
        fp.SetValue(comp['value'])

        # Position: stack in a grid to the right of the board
        x = place_x + (col_count % max_cols) * col_step
        y = place_y + (col_count // max_cols) * row_step
        fp.SetPosition(pcbnew.VECTOR2I(x, y))

        board.Add(fp)
        col_count += 1
        added += 1

    print(f'\nAdded {added} new footprints to PCB')

    if not_found:
        print(f'Footprint files not found ({len(not_found)}):')
        for s in not_found[:10]:
            print(f'  {s}')
        if len(not_found) > 10:
            print(f'  ... and {len(not_found)-10} more')

    # Save
    board.Save(str(PCB_FILE))
    print(f'\nSaved: {PCB_FILE}')
    print('Open PSN_TRX.kicad_pcb in KiCad PCBnew to arrange components.')


if __name__ == '__main__':
    main()

