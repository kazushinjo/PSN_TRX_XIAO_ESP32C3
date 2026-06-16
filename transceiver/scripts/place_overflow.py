#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew
from pathlib import Path

PCB_FILE = Path('/Users/kazuichishinjo/PSN_TRX_New/PSN_TRX.kicad_pcb')
mm = pcbnew.FromMM

# Current 14 overflow components from place_even_fill.py
OVERFLOW = ['C24', 'C31', 'LED1', 'MIC1', 'R11', 'R13', 'R20', 'R22', 'R23', 'R26', 'R27', 'R28', 'R29', 'R30']

BLOCKS = {
    'BPF_ANT':   ( 5,  5,  40,  47),
    'RF_AMP':    (42,  5,  77,  47),
    'VXO_MIX':  (79,  5, 112,  47),
    'PSN_AF':   (114,  5, 145,  47),
    'TX_CHAIN':  ( 5, 52,  44,  95),
    'RX_CHAIN':  (46, 52, 104,  95),
    'POWER':     (106,52, 145,  95),
}

board = pcbnew.LoadBoard(str(PCB_FILE))
if board is None:
    print('ERROR: cannot load PCB'); exit(1)

# Place in centre strip: y=49.5mm, x=10.5~137mm, 7mm pitch
STRIP_Y = 49.5
x_positions = [10.5 + i * 7.0 for i in range(20)]

print(f'Placing {len(OVERFLOW)} overflow in centre strip (y={STRIP_Y}mm)')
for i, ref in enumerate(OVERFLOW):
    fp = board.FindFootprintByReference(ref)
    if fp is None:
        print(f'  {ref}: not found')
        continue
    x = x_positions[i] if i < len(x_positions) else 10.5 + (i % 20) * 7.0
    fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(STRIP_Y)))
    fp.SetOrientationDegrees(0)
    print(f'  {ref} → ({x:.1f}, {STRIP_Y}mm)')

board.Save(str(PCB_FILE))
total = len(list(board.GetFootprints()))
print(f'\nSaved. Total footprints: {total}')
