#!/usr/bin/env python3
"""
Block-based component placement for PSN_TRX.kicad_pcb (150×100mm, 4-layer).

Board layout:
  ┌──────────────┬──────────────┬──────────────┐
  │  RF / VXO   │  PSN/Mixer  │   TX / BPF   │
  │  (5~60mm)   │  (63~100mm) │  (103~145mm) │
  ├──────────────┼──────────────┼──────────────┤
  │     RX      │  AF / Audio  │    Power     │
  │  (5~60mm)   │  (63~110mm) │  (113~145mm) │
  └──────────────┴──────────────┴──────────────┘
"""

import sys
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM

# ── Block bounding boxes (x1, y1, x2, y2) in mm ────────────────────────��────
BLOCKS = {
    'RF_VXO':    ( 5,  5,  57,  47),   # top-left
    'PSN_MIXER': (60,  5,  99,  47),   # top-center
    'TX_BPF':    (102, 5, 145,  47),   # top-right
    'RX':        ( 5, 52,  59,  95),   # bottom-left
    'AF':        (62, 52, 116,  95),   # bottom-center
    'POWER':     (118,52, 145,  95),   # bottom-right
}

# ── Component → block assignment ─────────────────────────────────────────────
ASSIGN = {
    # RF / VXO
    'Q1':   'RF_VXO',   # 3SK59 dual-gate FET
    'L1':   'RF_VXO',   'L2':   'RF_VXO',   # RF input coils
    'L3':   'RF_VXO',                        # VXO coil
    'X1':   'RF_VXO',                        # crystal
    'TC1':  'RF_VXO',   'TC2':  'RF_VXO',   'TC3':  'RF_VXO',
    'C1':   'RF_VXO',   'C2':   'RF_VXO',
    'C9':   'RF_VXO',   'C10':  'RF_VXO',
    'C13':  'RF_VXO',   'C17':  'RF_VXO',   'C18':  'RF_VXO',
    'C19':  'RF_VXO',   'C25':  'RF_VXO',   'C32':  'RF_VXO',
    'C3':   'RF_VXO',
    'VR2':  'RF_VXO',
    'D7':   'RF_VXO',   'D8':   'RF_VXO',
    'R2':   'RF_VXO',   'R3':   'RF_VXO',   'R4':   'RF_VXO',
    'R5':   'RF_VXO',

    # PSN / Mixer
    'D1':   'PSN_MIXER', 'D2':  'PSN_MIXER',
    'D3':   'PSN_MIXER', 'D4':  'PSN_MIXER',
    'L4':   'PSN_MIXER', 'L5':  'PSN_MIXER',
    'L6':   'PSN_MIXER', 'L7':  'PSN_MIXER',
    'C11':  'PSN_MIXER', 'C12': 'PSN_MIXER', 'C14':  'PSN_MIXER',
    'C23':  'PSN_MIXER', 'C24': 'PSN_MIXER', 'C31':  'PSN_MIXER',
    'C20':  'PSN_MIXER', 'C29': 'PSN_MIXER',
    'R1':   'PSN_MIXER', 'R36': 'PSN_MIXER',
    'R51':  'PSN_MIXER', 'R52': 'PSN_MIXER',
    'R6':   'PSN_MIXER', 'R7':  'PSN_MIXER',
    'Q14':  'PSN_MIXER',
    'C100': 'PSN_MIXER', 'C101':'PSN_MIXER',

    # TX / BPF
    'Q5':   'TX_BPF',
    'L11':  'TX_BPF',  'L12': 'TX_BPF',  'L13': 'TX_BPF',
    'L14':  'TX_BPF',  'L15': 'TX_BPF',
    'SW1':  'TX_BPF',
    'C4':   'TX_BPF',  'C6':  'TX_BPF',  'C7':  'TX_BPF',
    'R38':  'TX_BPF',  'R40': 'TX_BPF',  'R41': 'TX_BPF',  'R44': 'TX_BPF',
    'C102': 'TX_BPF',  'C103':'TX_BPF',  'C104':'TX_BPF',
    'R34':  'TX_BPF',  'R35': 'TX_BPF',

    # RX
    'Q9':   'RX', 'Q10':  'RX',
    'Q2':   'RX', 'Q3':   'RX', 'Q4':  'RX',
    'L8':   'RX', 'L9':   'RX', 'L10': 'RX',
    'C5':   'RX', 'C8':   'RX', 'C8b1':'RX',
    'R10':  'RX', 'R11':  'RX', 'R12': 'RX',
    'R13':  'RX', 'R15':  'RX', 'R16': 'RX',
    'C105': 'RX', 'C111': 'RX', 'C112':'RX',
    'Q7':   'RX', 'Q8':   'RX',   # 2SC1923 bias-related
    'R8':   'RX', 'R9':   'RX',

    # AF / Audio  (split large caps to POWER to reduce crowding)
    'T1':   'AF',
    'IC2':  'AF',
    'Q6':   'AF',
    'Q11':  'AF', 'Q12':  'AF', 'Q13': 'AF',
    'Q15':  'AF', 'Q17':  'AF',
    **{f'C{n}': 'AF' for n in range(158, 168)},
    'VR3':  'AF', 'VR4':  'AF', 'VR5': 'AF',
    'MIC1': 'AF',
    'LED1': 'AF', 'LED2': 'AF',
    'R18':  'AF', 'R20':  'AF', 'R21': 'AF', 'R22': 'AF',
    'R23':  'AF', 'R24':  'AF', 'R25': 'AF', 'R26': 'AF',
    'R27':  'AF', 'R28':  'AF', 'R29': 'AF', 'R30': 'AF',

    # Power supply (includes large bypass caps and AF power caps)
    'IC1':  'POWER', 'J1':  'POWER', 'VR1': 'POWER',
    'C28':  'POWER', 'C30': 'POWER',           # 100µF main bypass
    **{f'C{n}': 'POWER' for n in range(113, 127)},  # 0.01µF bypass
    'R31':  'POWER', 'R32': 'POWER', 'R33': 'POWER',
    'R42':  'POWER', 'R43': 'POWER',
    'R14':  'POWER', 'R17': 'POWER',
}

# Footprint → approximate cell size (w, h) in mm including 1mm padding
FP_CELL = {
    'PSN_TRX:L_FCZ07S_CT':                    (11, 11),
    'PSN_TRX:Transformer_ST71_CB19':           (24, 22),
    'PSN_TRX:L_T50_2pin_Vertical':             (12, 16),
    'PSN_TRX:L_T30_2pin_Vertical':             (10, 11),
    'PSN_TRX:L_T30_3pin_Vertical':             (10, 11),
    'PSN_TRX:L_AL0510-153K_Vertical':          ( 6,  6),
    'PSN_TRX:C_Trimmer_TMCV01':                ( 9,  8),
    'Package_TO_SOT_THT:TO-72-4':              ( 8,  8),
    'Package_TO_SOT_THT:TO-92_Inline':         ( 6,  7),
    'Package_DIP:DIP-8_W7.62mm':               (12,  9),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical': (5, 5),
    'Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm': (5, 5),
    'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm': (6, 6),
    'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm': ( 7,  7),
    'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm': ( 9,  9),
    'Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp': (4.5, 4.5),
    'LED_THT:LED_D3.0mm':                      ( 6,  6),
    'Crystal:Crystal_HC49-4H_Vertical':        ( 9,  9),
    'Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical': (11, 13),
    'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical': ( 6,  6),
    'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical': ( 9,  6),
    'Button_Switch_THT:SW_DIP_SPSTx01_Slide_6.7x4.1mm_W7.62mm_P2.54mm_LowProfile': (12, 7),
    'Button_Switch_THT:SW_E-Switch_EG1271_SPDT': (11, 8),
    'Relay_THT:Relay_DPDT_Omron_G5V-2':        (17, 13),
    'MountingHole:MountingHole_3.2mm_M3':      ( 0,  0),  # fixed, skip
    '_default':                                 ( 6,  6),
}


def cell_size(fp_str):
    if fp_str in FP_CELL:
        return FP_CELL[fp_str]
    for k, v in FP_CELL.items():
        if k != '_default' and (fp_str.endswith(k.split(':')[-1]) or k in fp_str):
            return v
    return FP_CELL['_default']


def place_block(board, refs, fp_map, area):
    """Row-pack components into the block area. Return list of overflows."""
    x1, y1, x2, y2 = area
    cx, cy = x1, y1
    row_h = 0
    overflows = []

    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        fp_str = fp_map.get(ref, '_default')
        w, h = cell_size(fp_str)
        if w == 0:
            continue  # mounting hole, skip

        if cx + w > x2:          # wrap row
            cy += row_h
            cx  = x1
            row_h = 0

        if cy + h > y2:           # overflow
            overflows.append(ref)
            continue

        fp.SetPosition(pcbnew.VECTOR2I(mm(cx + w/2), mm(cy + h/2)))
        fp.SetOrientationDegrees(0)
        cx += w
        row_h = max(row_h, h)

    return overflows


def main():
    print(f'Loading {PCB_FILE}')
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: Could not load PCB')
        return

    # Build ref → footprint string map
    fp_map = {fp.GetReference(): fp.GetFPIDAsString()
              for fp in board.GetFootprints()}

    # Invert ASSIGN to block → [refs]
    block_refs = {b: [] for b in BLOCKS}
    unassigned = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):   # mounting holes: already placed, skip
            continue
        block = ASSIGN.get(ref)
        if block:
            block_refs[block].append(ref)
        else:
            unassigned.append(ref)

    # Sort each block: large components first for better packing
    for block, refs in block_refs.items():
        refs.sort(key=lambda r: (-cell_size(fp_map.get(r,'_default'))[0] *
                                   cell_size(fp_map.get(r,'_default'))[1]))

    # Place each block
    all_overflows = []
    for block_name, area in BLOCKS.items():
        refs = block_refs[block_name]
        print(f'  {block_name:12s}: {len(refs):3d} comps  area={area}')
        ov = place_block(board, refs, fp_map, area)
        all_overflows.extend(ov)

    # Unassigned components → stack below the board
    overflow_x, overflow_y = 5.0, 105.0
    for i, ref in enumerate(unassigned + all_overflows):
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        fp.SetPosition(pcbnew.VECTOR2I(mm(overflow_x + (i % 20) * 7),
                                        mm(overflow_y + (i // 20) * 7)))

    board.Save(str(PCB_FILE))
    print(f'\nSaved {PCB_FILE}')
    print(f'Unassigned / overflow: {len(unassigned + all_overflows)} refs')
    if unassigned:
        print('  Unassigned:', sorted(unassigned)[:20])
    if all_overflows:
        print('  Overflow:  ', sorted(all_overflows)[:20])


if __name__ == '__main__':
    main()
