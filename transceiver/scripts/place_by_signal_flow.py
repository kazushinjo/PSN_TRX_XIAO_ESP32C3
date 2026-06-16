#!/usr/bin/env python3
"""
Signal-flow-based component placement for PSN_TRX (150×100mm, 4-layer).

Signal flow (left → right):
  Antenna/BPF → RF Amp → VXO/Mixer → PSN Network → AF/Audio

Layout:
  ┌───────────┬───────────┬────────────┬────────────┐
  │  BPF/Ant  │  RF Amp   │ VXO+Mixer  │  PSN/AF   │
  │ L11-L15   │ Q1,L1,L2  │ X1,L3,Q7  │ L4,L5,IC2 │
  │ TC3,SW1   │ TC1,TC2   │ D1-D4      │ T1,Q6-Q8  │
  │ L13 (TX)  │ Q9,Q10    │ L6,L7      │ VR3-5     │
  ├───────────┼───────────┼────────────┴────────────┤
  │  TX Path  │  RX Chain │    Power Supply         │
  │ Q5,Q14   │ Q2,Q3,Q4  │ IC1, J1, large caps     │
  │ D7,D8    │ L8-L10    │ bypass caps              │
  └───────────┴───────────┴─────────────────────────┘
"""

import sys
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM

# ── Block areas (x1, y1, x2, y2) mm ─────────────────────────────────────────
BLOCKS = {
    # Top row: signal path left→right
    'BPF_ANT':    ( 5,  5,  40,  48),  # BPF / antenna interface
    'RF_AMP':     (42,  5,  77,  48),  # RF amplifier
    'VXO_MIX':   (79,  5, 112,  48),  # VXO + diode ring mixer
    'PSN_AF':    (114,  5, 145,  48),  # PSN network + AF start

    # Bottom row
    'TX_CHAIN':   ( 5, 52,  50,  95),  # TX driver chain
    'RX_CHAIN':   (52, 52,  96,  95),  # RX amp / audio detection
    'POWER':      (98, 52, 145,  95),  # power supply + chokes
}

# ── Component → block ────────────────────────────────────────────────────────
ASSIGN = {
    # BPF / Antenna interface
    # L11: RX BPF input, L12: RX BPF, L13: driver output / RX BPF
    # L14, L15: TX output toroids
    'L11':  'BPF_ANT', 'L12': 'BPF_ANT', 'L13': 'BPF_ANT',
    'L14':  'BPF_ANT', 'L15': 'BPF_ANT',
    'TC3':  'BPF_ANT',
    'SW1':  'BPF_ANT',
    'C24':  'BPF_ANT', 'C31': 'BPF_ANT',   # BPF coupling caps

    # RF Amplifier (Q1: 3SK59 dual-gate MOSFET)
    'Q1':   'RF_AMP',
    'L1':   'RF_AMP',  'L2':  'RF_AMP',    # RF coupling coils (FCZ)
    'TC1':  'RF_AMP',  'TC2': 'RF_AMP',    # RF tuning trimmers
    'Q9':   'RF_AMP',  'Q10': 'RF_AMP',    # 2SK439 RX FETs
    'C1':   'RF_AMP',  'C2':  'RF_AMP',
    'C9':   'RF_AMP',  'C10': 'RF_AMP',
    'R1':   'RF_AMP',  'R2':  'RF_AMP',
    'VR1':  'RF_AMP',                       # AGC/bias adj (panel header)

    # VXO + Diode ring mixer
    'X1':   'VXO_MIX',                      # VXO crystal
    'L3':   'VXO_MIX',                      # VXO coil
    'Q7':   'VXO_MIX',                      # VXO buffer (2SC1923)
    'D1':   'VXO_MIX', 'D2': 'VXO_MIX',    # diode ring mixer
    'D3':   'VXO_MIX', 'D4': 'VXO_MIX',
    'L6':   'VXO_MIX', 'L7': 'VXO_MIX',   # PSN coils (FCZ)
    'C3':   'VXO_MIX', 'C17':'VXO_MIX',
    'C18':  'VXO_MIX', 'C19':'VXO_MIX',
    'C23':  'VXO_MIX',
    'R16':  'VXO_MIX', 'R17':'VXO_MIX',
    'VR2':  'VXO_MIX',                      # VXO freq adj (panel header)
    'C25':  'VXO_MIX',

    # PSN network + AF start
    'L4':   'PSN_AF',  'L5':  'PSN_AF',    # T-30 PSN toroids
    'IC2':  'PSN_AF',                       # NJM2904 op-amp (PSN)
    'Q8':   'PSN_AF',                       # 2SC1923 phase buffer
    'Q14':  'PSN_AF',                       # 2SK439
    'C11':  'PSN_AF',  'C12': 'PSN_AF',
    'C13':  'PSN_AF',  'C14': 'PSN_AF',
    'C20':  'PSN_AF',  'C29': 'PSN_AF',
    'R3':   'PSN_AF',  'R4':  'PSN_AF',
    'R5':   'PSN_AF',  'R6':  'PSN_AF',
    'R36':  'PSN_AF',
    'C100': 'PSN_AF',  'C101':'PSN_AF',

    # TX chain (Q5: 2SC2120 TX driver, D7/D8: TX carrier suppression)
    'Q5':   'TX_CHAIN',
    'D7':   'TX_CHAIN', 'D8': 'TX_CHAIN',
    'Q15':  'TX_CHAIN',
    'C32':  'TX_CHAIN',
    'R38':  'TX_CHAIN', 'R40':'TX_CHAIN',
    'R41':  'TX_CHAIN', 'R44':'TX_CHAIN',
    'R34':  'TX_CHAIN', 'R35':'TX_CHAIN',
    'R51':  'TX_CHAIN', 'R52':'TX_CHAIN',
    'C4':   'TX_CHAIN', 'C6': 'TX_CHAIN',  'C7':  'TX_CHAIN',
    'C102': 'TX_CHAIN', 'C103':'TX_CHAIN', 'C104':'TX_CHAIN',
    'VR4':  'TX_CHAIN', 'VR5':'TX_CHAIN',  # TX balance trimmers

    # RX chain + AF detection
    'Q2':   'RX_CHAIN',                    # 2SC1923 RX IF amp
    'Q3':   'RX_CHAIN', 'Q4': 'RX_CHAIN', # 2SC1815
    'Q6':   'RX_CHAIN',                    # 2SA950 AF output
    'Q11':  'RX_CHAIN', 'Q12':'RX_CHAIN',
    'Q13':  'RX_CHAIN',
    'Q17':  'RX_CHAIN',
    'T1':   'RX_CHAIN',                    # ST-71 audio transformer
    'Q16': 'RX_CHAIN',                     # if exists
    'R7':   'RX_CHAIN', 'R8': 'RX_CHAIN',
    'R9':   'RX_CHAIN', 'R10':'RX_CHAIN',
    'R11':  'RX_CHAIN', 'R12':'RX_CHAIN',
    'R13':  'RX_CHAIN', 'R15':'RX_CHAIN',
    'R18':  'RX_CHAIN', 'R20':'RX_CHAIN',
    'R21':  'RX_CHAIN', 'R22':'RX_CHAIN',
    'R23':  'RX_CHAIN', 'R24':'RX_CHAIN',
    'R25':  'RX_CHAIN', 'R26':'RX_CHAIN',
    'R27':  'RX_CHAIN', 'R28':'RX_CHAIN',
    'R29':  'RX_CHAIN', 'R30':'RX_CHAIN',
    'VR3':  'RX_CHAIN',                    # AF volume (on-board)
    'MIC1': 'RX_CHAIN',                    # mic connector
    'LED1': 'RX_CHAIN', 'LED2':'RX_CHAIN',
    **{f'C{n}': 'RX_CHAIN' for n in range(158, 168)},
    'C28':  'RX_CHAIN', 'C30':'RX_CHAIN',

    # Power supply
    'IC1':  'POWER',   'J1':  'POWER',
    'L8':   'POWER',   'L9':  'POWER',   'L10': 'POWER',
    'C5':   'POWER',   'C8':  'POWER',   'C8b1':'POWER',
    **{f'C{n}': 'POWER' for n in range(105, 127)},
    'R14':  'POWER',   'R17': 'POWER',
    'R31':  'POWER',   'R32': 'POWER',   'R33': 'POWER',
    'R42':  'POWER',   'R43': 'POWER',
    'Q16':  'POWER',
    'C33':  'POWER',
}

# ── Footprint cell sizes (w × h mm, includes ~0.5mm padding) ─────────────────
FP_CELL = {
    'PSN_TRX:L_FCZ07S_CT':                    (10, 10),
    'PSN_TRX:Transformer_ST71_CB19':           (23, 21),
    'PSN_TRX:L_T50_2pin_Vertical':             (11, 15),
    'PSN_TRX:L_T30_2pin_Vertical':             ( 9, 10),
    'PSN_TRX:L_T30_3pin_Vertical':             ( 9, 10),
    'PSN_TRX:L_AL0510-153K_Vertical':          ( 5,  5),
    'PSN_TRX:C_Trimmer_TMCV01':                ( 8,  7),
    'Package_TO_SOT_THT:TO-72-4':              ( 7,  7),
    'Package_TO_SOT_THT:TO-92_Inline':         ( 5,  6),
    'Package_DIP:DIP-8_W7.62mm':               (11,  8),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical': (4.5, 4.5),
    'Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm': (5, 5),
    'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm': (6, 6),
    'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm': ( 7,  7),
    'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm': ( 9,  9),
    'Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp': (4.5, 4.5),
    'LED_THT:LED_D3.0mm':                      ( 5,  5),
    'Crystal:Crystal_HC49-4H_Vertical':        ( 8,  8),
    'Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical': (11, 13),
    'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical': ( 5,  5),
    'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical': ( 8,  5),
    'Button_Switch_THT:SW_DIP_SPSTx01_Slide_6.7x4.1mm_W7.62mm_P2.54mm_LowProfile': (11, 6),
    'Button_Switch_THT:SW_E-Switch_EG1271_SPDT': (10, 7),
    'Relay_THT:Relay_DPDT_Omron_G5V-2':        (16, 12),
    'MountingHole:MountingHole_3.2mm_M3':      ( 0,  0),
    '_default':                                 ( 6,  6),
}

def cell_wh(fp_str):
    if fp_str in FP_CELL:
        return FP_CELL[fp_str]
    for k, v in FP_CELL.items():
        if k != '_default' and k in fp_str:
            return v
    return FP_CELL['_default']

def place_block(board, refs, fp_map, area, label):
    x1, y1, x2, y2 = area
    cx, cy, row_h = x1, y1, 0
    overflows = []
    placed = 0
    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        w, h = cell_wh(fp_map.get(ref, '_default'))
        if w == 0:
            continue
        if cx + w > x2:
            cy += row_h; cx = x1; row_h = 0
        if cy + h > y2:
            overflows.append(ref); continue
        fp.SetPosition(pcbnew.VECTOR2I(mm(cx + w/2), mm(cy + h/2)))
        fp.SetOrientationDegrees(0)
        cx += w; row_h = max(row_h, h); placed += 1
    return placed, overflows

def main():
    print(f'Loading {PCB_FILE}')
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: Could not load PCB'); return

    fp_map = {fp.GetReference(): fp.GetFPIDAsString()
              for fp in board.GetFootprints()}

    # Sort: large first
    def sort_key(ref):
        w, h = cell_wh(fp_map.get(ref, '_default'))
        return -(w * h)

    # Build block lists
    block_refs = {b: [] for b in BLOCKS}
    unassigned = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        blk = ASSIGN.get(ref)
        if blk and blk in block_refs:
            block_refs[blk].append(ref)
        else:
            unassigned.append(ref)

    for blk in block_refs:
        block_refs[blk].sort(key=sort_key)

    total_placed = 0
    all_overflow = []
    print('\n  Block            comps  placed  overflow  area')
    print('  ' + '─'*55)
    for blk, area in BLOCKS.items():
        refs = block_refs[blk]
        p, ov = place_block(board, refs, fp_map, area, blk)
        total_placed += p
        all_overflow.extend(ov)
        w = area[2]-area[0]; h = area[3]-area[1]
        print(f'  {blk:15s}  {len(refs):4d}   {p:4d}    {len(ov):4d}    '
              f'{w:.0f}×{h:.0f}mm')

    # Place overflow + unassigned below board
    ov_refs = unassigned + all_overflow
    for i, ref in enumerate(ov_refs):
        fp = board.FindFootprintByReference(ref)
        if fp is None: continue
        fp.SetPosition(pcbnew.VECTOR2I(
            mm(5 + (i % 25) * 6), mm(103 + (i // 25) * 6)))

    board.Save(str(PCB_FILE))
    print(f'\n  Total placed on board: {total_placed}')
    print(f'  Below-board (adjust manually): {len(ov_refs)}')
    if ov_refs:
        print(f'    {sorted(ov_refs)[:20]}')

if __name__ == '__main__':
    main()
