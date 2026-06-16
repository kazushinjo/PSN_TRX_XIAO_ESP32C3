#!/usr/bin/env python3
"""
Create PSN_TRX.kicad_pcb using KiCad Python API:
  - 4-layer stackup (JLCPCB JLC7628, 1.6mm)
  - 150 x 100 mm board outline
  - M3 mounting holes at corners
  - All footprints from netlist placed (stacked outside board for manual arrangement)

Run with:
  /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 create_pcb_api.py
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
NET_FILE    = PROJECT_DIR / 'PSN_TRX.net'

W_MM, H_MM  = 150.0, 100.0   # board size
CORNER_MM   = 3.5             # mounting hole offset from edge

FP_SEARCH = [
    PROJECT_DIR,   # local: PROJECT_DIR/PSN_TRX.pretty/xxx.kicad_mod
    Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'),
    Path.home() / 'Library/Application Support/kicad/9.0/footprints',
    Path.home() / 'Library/Application Support/kicad/10.0/footprints',
]

mm = pcbnew.FromMM


def find_fp_file(lib_ref: str):
    if ':' not in lib_ref:
        return None
    lib_name, fp_name = lib_ref.split(':', 1)
    for base in FP_SEARCH:
        p = base / f'{lib_name}.pretty' / f'{fp_name}.kicad_mod'
        if p.exists():
            return base / f'{lib_name}.pretty', fp_name
    return None


def parse_netlist(path: Path):
    c = path.read_text(encoding='utf-8')
    result = []
    for m in re.finditer(
        r'\(comp\s+\(ref\s+"([^"]+)"\)'
        r'(?:(?!\(comp\s).)*?\(value\s+"([^"]+)"\)'
        r'(?:(?!\(comp\s).)*?\(footprint\s+"([^"]+)"\)',
        c, re.DOTALL
    ):
        ref, val, fp = m.group(1), m.group(2), m.group(3)
        if fp:
            result.append((ref, val, fp))
    return result


def setup_layers(board):
    """Enable 4 layers and set stackup."""
    board.SetCopperLayerCount(4)

    enabled = board.GetEnabledLayers()
    enabled.AddLayer(pcbnew.In1_Cu)
    enabled.AddLayer(pcbnew.In2_Cu)
    board.SetEnabledLayers(enabled)

    board.SetLayerName(pcbnew.In1_Cu, 'GND Plane')
    board.SetLayerName(pcbnew.In2_Cu, 'Power Plane')

    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))

    print('  Layers: F.Cu / In1.Cu(GND) / In2.Cu(Power) / B.Cu')


def add_board_outline(board):
    """Draw 150×100mm board edge."""
    corners = [
        (0, 0), (W_MM, 0), (W_MM, H_MM), (0, H_MM), (0, 0),
    ]
    for i in range(len(corners) - 1):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.05))
        x1, y1 = corners[i]
        x2, y2 = corners[i + 1]
        seg.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        seg.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        board.Add(seg)
    print(f'  Board outline: {W_MM}×{H_MM} mm')


def add_mounting_holes(board):
    """Place M3 non-plated through-holes at 4 corners."""
    corners = [
        ('H1', CORNER_MM,           CORNER_MM),
        ('H2', W_MM - CORNER_MM,    CORNER_MM),
        ('H3', CORNER_MM,           H_MM - CORNER_MM),
        ('H4', W_MM - CORNER_MM,    H_MM - CORNER_MM),
    ]
    fp_dir = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/MountingHole.pretty')
    for ref, x, y in corners:
        fp = pcbnew.FootprintLoad(str(fp_dir), 'MountingHole_3.2mm_M3')
        if fp is None:
            print(f'  WARNING: MountingHole_3.2mm_M3 not found')
            continue
        fp.SetReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        fp.SetAttributes(pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
        board.Add(fp)
    print(f'  Mounting holes: H1-H4 at corners (offset {CORNER_MM}mm)')


def add_netlist_footprints(board, components):
    """Add all footprints from netlist, stacked outside board for manual placement."""
    col, row = 0, 0
    per_row = 15
    start_x = W_MM + 10
    start_y = 5
    step = 6.0

    added, missing = 0, []

    for ref, val, fp_ref in components:
        loc = find_fp_file(fp_ref)
        if loc is None:
            missing.append(f'{ref}: {fp_ref}')
            continue
        fp_dir, fp_name = loc
        fp = pcbnew.FootprintLoad(str(fp_dir), fp_name)
        if fp is None:
            missing.append(f'{ref}: load failed')
            continue

        fp.SetReference(ref)
        fp.SetValue(val)
        x = mm(start_x + (col % per_row) * step)
        y = mm(start_y + (col // per_row) * step)
        fp.SetPosition(pcbnew.VECTOR2I(x, y))
        board.Add(fp)
        col += 1
        added += 1

    print(f'  Components added: {added}/{len(components)}')
    if missing:
        print(f'  Missing footprints ({len(missing)}):')
        for s in missing[:8]:
            print(f'    {s}')
        if len(missing) > 8:
            print(f'    ... +{len(missing)-8} more')
    return missing


def main():
    print('Creating PSN_TRX.kicad_pcb ...')

    # Back up existing file
    if PCB_FILE.exists():
        PCB_FILE.rename(PCB_FILE.with_suffix('.kicad_pcb.bak_api'))

    board = pcbnew.NewBoard(str(PCB_FILE))

    print('Setting up 4-layer stackup...')
    setup_layers(board)

    print('Adding board outline...')
    add_board_outline(board)

    print('Adding mounting holes...')
    add_mounting_holes(board)

    print('Loading netlist and placing footprints...')
    components = parse_netlist(NET_FILE)
    print(f'  Netlist: {len(components)} components')
    missing = add_netlist_footprints(board, components)

    board.Save(str(PCB_FILE))
    print(f'\nSaved: {PCB_FILE}')
    print(f'Total footprints in PCB: {len(list(board.GetFootprints()))}')
    print('\nNext: Open PSN_TRX.kicad_pcb in KiCad PCBnew')
    print('  - Run DRC to check design rules')
    print('  - Arrange components by functional block')
    print('  - Route traces (manual or auto-router)')
    if missing:
        print(f'\nWARNING: {len(missing)} footprints not found. Add library paths if needed.')


if __name__ == '__main__':
    main()
