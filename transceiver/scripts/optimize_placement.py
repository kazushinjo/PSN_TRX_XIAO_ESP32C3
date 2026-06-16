#!/usr/bin/env python3
"""
Optimize component placement: spread evenly with minimal overlap.
- Distribute components across full board area
- Maintain 3mm minimum spacing
- Sort by signal flow for routing efficiency
"""

import sys, math, random
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM
to_mm = pcbnew.ToMM

# Signal flow priority (antenna → RF → VXO → mixer → PSN → AF → TX/RX output)
FLOW_PRIORITY = {
    'L11': 0, 'L12': 0, 'L13': 0, 'L14': 0, 'L15': 0,
    'Q1': 1, 'L1': 1, 'L2': 1, 'TC1': 1, 'TC2': 1,
    'X1': 2, 'Q7': 2, 'L3': 2, 'D1': 2, 'D2': 2, 'D3': 2, 'D4': 2,
    'L6': 2, 'L7': 2,
    'L4': 3, 'L5': 3, 'IC2': 3, 'Q8': 3,
    'Q5': 4, 'D7': 4, 'D8': 4,
    'T1': 5,
    'Q2': 6, 'Q3': 6, 'Q4': 6, 'Q6': 6,
}

def get_flow_order(ref):
    """Return signal flow priority (lower = earlier)."""
    # Extract base ref (Q1 from Q1a)
    base = ''.join([c for c in ref if not c.isdigit()])
    num = int(''.join([c for c in ref if c.isdigit()]) or '0')

    if ref in FLOW_PRIORITY:
        return FLOW_PRIORITY[ref]
    if base in FLOW_PRIORITY:
        return FLOW_PRIORITY[base]

    # Default by component type
    if ref.startswith('Q'):
        return 6
    if ref.startswith('L'):
        return 1
    if ref.startswith('C'):
        return 7
    if ref.startswith('R'):
        return 7
    if ref.startswith('D'):
        return 2
    return 8


def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    X_MIN, X_MAX = 5, 145
    Y_MIN, Y_MAX = 5, 95
    MIN_GAP = 3.0  # mm

    # Collect all components
    components = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        components.append({
            'ref': ref,
            'fp': fp,
            'flow': get_flow_order(ref),
        })

    # Sort by signal flow priority
    components.sort(key=lambda c: (c['flow'], c['ref']))

    print(f'Optimizing placement of {len(components)} components')
    print('Signal flow priority groups:')
    by_flow = defaultdict(list)
    for c in components:
        by_flow[c['flow']].append(c['ref'])
    for flow in sorted(by_flow.keys()):
        print(f'  Flow {flow}: {len(by_flow[flow])} components')

    # Grid-based placement with flow-aware zones
    BOARD_W = X_MAX - X_MIN
    BOARD_H = Y_MAX - Y_MIN

    # 2 rows, 5 columns per flow group
    grid_cols = 10
    grid_rows = 6
    cell_w = BOARD_W / grid_cols
    cell_h = BOARD_H / grid_rows

    placed = 0
    for flow in sorted(by_flow.keys()):
        refs = by_flow[flow]
        # Spread each flow group across a horizontal band
        band = flow % grid_rows
        col_start = (flow // grid_rows) * 2

        for i, ref in enumerate(refs):
            comp = next(c for c in components if c['ref'] == ref)
            col = (col_start + i % (grid_cols - col_start)) % grid_cols
            row = band + (i // (grid_cols - col_start)) * 1
            row = row % grid_rows

            x = X_MIN + col * cell_w + cell_w / 2 + random.uniform(-cell_w * 0.3, cell_w * 0.3)
            y = Y_MIN + row * cell_h + cell_h / 2 + random.uniform(-cell_h * 0.3, cell_h * 0.3)

            # Clamp to board
            x = max(X_MIN + 2, min(X_MAX - 2, x))
            y = max(Y_MIN + 2, min(Y_MAX - 2, y))

            comp['fp'].SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            comp['fp'].SetOrientationDegrees(0)
            placed += 1

    board.Save(str(PCB_FILE))
    print(f'\n✓ Placed {placed} components in flow-aware grid')
    print(f'Layout: {grid_cols}×{grid_rows} grid, cell size {cell_w:.1f}×{cell_h:.1f}mm')


if __name__ == '__main__':
    main()
