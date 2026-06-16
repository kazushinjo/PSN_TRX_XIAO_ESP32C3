#!/usr/bin/env python3
"""
Enlarge board and rescale component placement to reduce DRC violations.
Current: 150×100mm → New: 220×150mm (1.5× scale)
"""

import sys, re
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM
to_mm = pcbnew.ToMM

# Current and new board dimensions (mm)
OLD_X_MIN, OLD_X_MAX = 5, 145
OLD_Y_MIN, OLD_Y_MAX = 5, 95
OLD_W = OLD_X_MAX - OLD_X_MIN  # 140mm
OLD_H = OLD_Y_MAX - OLD_Y_MIN  # 90mm

NEW_X_MIN, NEW_X_MAX = 5, 225
NEW_Y_MIN, NEW_Y_MAX = 5, 155
NEW_W = NEW_X_MAX - NEW_X_MIN  # 220mm
NEW_H = NEW_Y_MAX - NEW_Y_MIN  # 150mm

SCALE_X = NEW_W / OLD_W  # 1.571
SCALE_Y = NEW_H / OLD_H  # 1.667

def rescale_position(x, y):
    """Rescale component position to larger board."""
    # Map old coordinates to new coordinates
    rel_x = (x - OLD_X_MIN) / OLD_W
    rel_y = (y - OLD_Y_MIN) / OLD_H
    new_x = NEW_X_MIN + rel_x * NEW_W
    new_y = NEW_Y_MIN + rel_y * NEW_H
    return new_x, new_y

def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    print(f'Current board: {OLD_X_MIN}-{OLD_X_MAX} x {OLD_Y_MIN}-{OLD_Y_MAX} mm ({OLD_W}×{OLD_H})')
    print(f'New board: {NEW_X_MIN}-{NEW_X_MAX} x {NEW_Y_MIN}-{NEW_Y_MAX} mm ({NEW_W}×{NEW_H})')
    print(f'Scale: {SCALE_X:.2f}× (X), {SCALE_Y:.2f}× (Y)')

    # Rescale all components
    moved = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        old_x = to_mm(fp.GetPosition().x)
        old_y = to_mm(fp.GetPosition().y)

        new_x, new_y = rescale_position(old_x, old_y)
        fp.SetPosition(pcbnew.VECTOR2I(mm(new_x), mm(new_y)))
        moved += 1

    # Update mounting holes to new corners
    holes = {
        'H1': (NEW_X_MIN + 3, NEW_Y_MIN + 3),
        'H2': (NEW_X_MAX - 3, NEW_Y_MIN + 3),
        'H3': (NEW_X_MIN + 3, NEW_Y_MAX - 3),
        'H4': (NEW_X_MAX - 3, NEW_Y_MAX - 3),
    }

    for ref, (x, y) in holes.items():
        hole = board.FindFootprintByReference(ref)
        if hole:
            hole.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))

    # Update board outline (Edge.Cuts layer)
    # This is more complex and would need custom S-expression editing
    # For now, just save the rescaled positions

    board.Save(str(PCB_FILE))
    print(f'\n✓ Rescaled {moved} components')
    print(f'✓ Updated mounting holes to new corners')
    print(f'✓ Saved {PCB_FILE}')

    # Now update board outline in the file
    print('\nUpdating board outline...')
    with open(PCB_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and update board outline dimensions
    # Old outline: approximately from (5,5) to (145,95)
    # Replace with new dimensions (5,5) to (225,155)
    old_outline_pattern = r'(\(fp_rect\s+\(start\s+[0-9.]+\s+[0-9.]+\)?\s+\(end\s+[0-9.]+\s+[0-9.]+\))'

    # More reliable: replace specific outline coordinates
    content = content.replace('(start 5 5)', f'(start {NEW_X_MIN} {NEW_Y_MIN})')
    content = content.replace('(end 145 95)', f'(end {NEW_X_MAX} {NEW_Y_MAX})')

    with open(PCB_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print('✓ Board outline updated')


if __name__ == '__main__':
    main()
