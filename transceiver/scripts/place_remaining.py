#!/usr/bin/env python3
"""
Place remaining unpositioned components in available board space.
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

    # Find components outside board or below board (y > 100)
    X_MIN, X_MAX = 5, 145
    Y_MIN, Y_MAX = 5, 95
    BELOW_BOARD = 100

    unpositioned = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        x = to_mm(fp.GetPosition().x)
        y = to_mm(fp.GetPosition().y)

        # Check if outside board area
        if not (X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX):
            unpositioned.append((ref, fp, x, y))

    print(f'Found {len(unpositioned)} unpositioned components')
    if not unpositioned:
        print('All components already positioned!')
        board.Save(str(PCB_FILE))
        return

    # Collect occupied positions on board
    occupied = set()
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        x = to_mm(fp.GetPosition().x)
        y = to_mm(fp.GetPosition().y)
        if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
            # Mark a 10mm radius as occupied
            occupied.add((round(x), round(y)))

    # Place in available gaps using a spiral search
    placed = 0
    for ref, fp, old_x, old_y in sorted(unpositioned):
        placed_here = False

        # Try to find a free spot near the board center, spiraling outward
        center_x = (X_MIN + X_MAX) / 2
        center_y = (Y_MIN + Y_MAX) / 2

        for radius in range(0, 100, 5):
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                x = center_x + radius * math.cos(rad)
                y = center_y + radius * math.sin(rad)

                # Check bounds
                if not (X_MIN + 3 <= x <= X_MAX - 3 and Y_MIN + 3 <= y <= Y_MAX - 3):
                    continue

                # Check if occupied
                cell = (round(x), round(y))
                if cell not in occupied:
                    fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
                    fp.SetOrientationDegrees(0)
                    occupied.add(cell)
                    print(f'  {ref} → ({x:.1f}, {y:.1f})mm')
                    placed += 1
                    placed_here = True
                    break

            if placed_here:
                break

        if not placed_here:
            # Fallback: place in a grid at the bottom edge of board
            col = placed % 8
            row = placed // 8
            x = X_MIN + 5 + col * 15
            y = Y_MAX - 5 - row * 8
            fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
            print(f'  {ref} → ({x:.1f}, {y:.1f})mm (fallback)')
            placed += 1

    board.Save(str(PCB_FILE))
    print(f'\nPlaced {placed}/{len(unpositioned)} components')

    # Verify final state
    on_board = 0
    still_outside = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        x = to_mm(fp.GetPosition().x)
        y = to_mm(fp.GetPosition().y)
        if X_MIN <= x <= X_MAX and Y_MIN <= y <= Y_MAX:
            on_board += 1
        else:
            still_outside.append(ref)

    print(f'\n✓ Final: {on_board}/157 components on board')
    if still_outside:
        print(f'Still outside: {sorted(still_outside)}')


if __name__ == '__main__':
    main()
