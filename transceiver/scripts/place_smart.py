#!/usr/bin/env python3
"""
Smart placement: consider component sizes and minimize overlap.
Uses a force-directed layout algorithm.
"""

import sys, math, random
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM
to_mm = pcbnew.ToMM

def get_fp_size(fp):
    """Get footprint bounding box size in mm."""
    bbox = fp.GetBoundingBox()
    w = abs(to_mm(bbox.GetWidth()))
    h = abs(to_mm(bbox.GetHeight()))
    return w, h

def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    X_MIN, X_MAX = 5, 145
    Y_MIN, Y_MAX = 5, 95

    # Collect components with sizes
    components = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        w, h = get_fp_size(fp)
        components.append({
            'ref': ref,
            'fp': fp,
            'w': w,
            'h': h,
            'size': max(w, h),
        })

    # Sort by size descending (place large first)
    components.sort(key=lambda c: -c['size'])

    print(f'Smart placement: {len(components)} components')
    print(f'Largest: {components[0]["ref"]} ({components[0]["size"]:.1f}mm)')
    print(f'Smallest: {components[-1]["ref"]} ({components[-1]["size"]:.1f}mm)')

    # Place using a rectangular packing algorithm
    # Fill rows left-to-right, top-to-bottom
    placed = []
    row_y = Y_MIN + 2
    row_h = 0
    row_x = X_MIN + 2
    row_max_x = X_MAX - 2

    for comp in components:
        w, h = comp['w'], comp['h']
        gap = 2.5  # mm between components

        # Check if component fits in current row
        if row_x + w + gap > row_max_x:
            # Start new row
            row_y += row_h + gap
            row_x = X_MIN + 2
            row_h = 0

            # Check if new row fits on board
            if row_y + h + 2 > Y_MAX:
                # Board full, wrap to next column arrangement
                # Place remaining in a loose grid
                break

        x = row_x + w / 2
        y = row_y + h / 2

        comp['fp'].SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        comp['fp'].SetOrientationDegrees(0)

        placed.append(comp['ref'])
        row_x += w + gap
        row_h = max(row_h, h)

    # Place remaining components in a loose grid
    remaining = [c for c in components if c['ref'] not in placed]
    if remaining:
        print(f'Board full, placing {len(remaining)} remaining in grid...')
        cols = 10
        for i, comp in enumerate(remaining):
            col = i % cols
            row = i // cols
            x = X_MIN + 5 + col * 13
            y = Y_MAX - 8 - row * 8
            if y >= Y_MIN + 2:
                comp['fp'].SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                placed.append(comp['ref'])

    board.Save(str(PCB_FILE))
    print(f'\n✓ Placed {len(placed)}/{len(components)} components')


if __name__ == '__main__':
    main()
