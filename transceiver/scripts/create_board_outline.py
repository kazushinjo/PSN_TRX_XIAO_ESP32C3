#!/usr/bin/env python3
"""
Create proper board outline (Edge.Cuts) for 220×150mm board.
Adds rectangular border at board edges.
"""

import sys
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM

def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    # Remove existing Edge.Cuts (if any)
    for item in board.GetDrawings():
        if item.GetLayer() == pcbnew.Edge_Cuts:
            board.Delete(item)

    # Create 220×150mm rectangular outline
    X_MIN, X_MAX = 5, 225
    Y_MIN, Y_MAX = 5, 155

    # Create 4 line segments forming a rectangle
    lines = [
        ((X_MIN, Y_MIN), (X_MAX, Y_MIN)),  # Top
        ((X_MAX, Y_MIN), (X_MAX, Y_MAX)),  # Right
        ((X_MAX, Y_MAX), (X_MIN, Y_MAX)),  # Bottom
        ((X_MIN, Y_MAX), (X_MIN, Y_MIN)),  # Left
    ]

    for (x1, y1), (x2, y2) in lines:
        line = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        line.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        line.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
        line.SetLayer(pcbnew.Edge_Cuts)
        line.SetWidth(mm(0.1))  # 0.1mm line width
        board.Add(line)

    # Add mounting hole markers (Edge.Cuts layer)
    # Note: actual holes are in H1-H4 footprints
    holes = [(8, 8), (222, 8), (8, 152), (222, 152)]
    for x, y in holes:
        circle = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_CIRCLE)
        circle.SetCenter(pcbnew.VECTOR2I(mm(x), mm(y)))
        circle.SetEnd(pcbnew.VECTOR2I(mm(x + 1.6), mm(y)))  # 3.2mm diameter
        circle.SetLayer(pcbnew.Edge_Cuts)
        circle.SetWidth(mm(0.1))
        board.Add(circle)

    board.Save(str(PCB_FILE))
    print('✓ Board outline created:')
    print(f'  Rectangle: (5, 5) to (225, 155) mm')
    print(f'  Size: 220×150 mm')
    print(f'  M3 holes: 4 corners')
    print(f'✓ Saved {PCB_FILE}')


if __name__ == '__main__':
    main()
