#!/usr/bin/env python3
"""
Final placement: maximize spacing to minimize DRC violations.
Use larger grid cells with centered components.
"""

import sys, math
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM
to_mm = pcbnew.ToMM

def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    X_MIN, X_MAX = 5, 145
    Y_MIN, Y_MAX = 5, 95

    # Collect components
    components = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        components.append({'ref': ref, 'fp': fp})

    # Sort by reference for consistency
    components.sort(key=lambda c: c['ref'])

    # Large grid cells with 8mm spacing between cell centers
    # 4×8 grid = 32 slots
    COLS = 7
    ROWS = 6
    CELL_W = (X_MAX - X_MIN) / COLS
    CELL_H = (Y_MAX - Y_MIN) / ROWS

    print(f'Placing {len(components)} components in {COLS}×{ROWS} grid')
    print(f'Cell size: {CELL_W:.1f}×{CELL_H:.1f}mm')

    for i, comp in enumerate(components):
        col = i % COLS
        row = (i // COLS) % ROWS

        # Center of cell with small random offset for visual variety
        x = X_MIN + (col + 0.5) * CELL_W
        y = Y_MIN + (row + 0.5) * CELL_H

        comp['fp'].SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        comp['fp'].SetOrientationDegrees(0)

    board.Save(str(PCB_FILE))
    print(f'✓ Placed all {len(components)} components')


if __name__ == '__main__':
    main()
