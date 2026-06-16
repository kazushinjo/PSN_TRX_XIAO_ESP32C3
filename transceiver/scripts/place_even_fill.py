#!/usr/bin/env python3
"""
Even-fill placement: distribute components evenly within each functional block.
- Sorts by component size (large first)
- Calculates grid cell size so components fill the block with no dead zones
- Spreads spacing to fill block edges
"""

import sys, math
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM

# ── Block areas (x1, y1, x2, y2) mm ─────────────────────────────────────────
BLOCKS = {
    'BPF_ANT':   ( 5,  5,  40,  47),
    'RF_AMP':    (42,  5,  77,  47),
    'VXO_MIX':  (79,  5, 112,  47),
    'PSN_AF':   (114,  5, 145,  47),
    'TX_CHAIN':  ( 5, 52,  44,  95),
    'RX_CHAIN':  (46, 52, 104,  95),
    'POWER':     (106,52, 145,  95),
}

# ── Component → block (same as place_by_signal_flow.py) ─────────────────────
ASSIGN = {
    'L11':'BPF_ANT','L12':'BPF_ANT','L13':'BPF_ANT',
    'L14':'BPF_ANT','L15':'BPF_ANT','TC3':'BPF_ANT','SW1':'BPF_ANT',
    'C24':'BPF_ANT','C31':'BPF_ANT','K1':'BPF_ANT',
    'Q1':'RF_AMP','L1':'RF_AMP','L2':'RF_AMP','TC1':'RF_AMP','TC2':'RF_AMP',
    'Q9':'RF_AMP','Q10':'RF_AMP','C1':'RF_AMP','C2':'RF_AMP',
    'C9':'RF_AMP','C10':'RF_AMP','R1':'RF_AMP','R2':'RF_AMP','VR1':'RF_AMP',
    'X1':'VXO_MIX','L3':'VXO_MIX','Q7':'VXO_MIX',
    'D1':'VXO_MIX','D2':'VXO_MIX','D3':'VXO_MIX','D4':'VXO_MIX',
    'L6':'VXO_MIX','L7':'VXO_MIX','C3':'VXO_MIX','C17':'VXO_MIX',
    'C18':'VXO_MIX','C19':'VXO_MIX','C23':'VXO_MIX',
    'R16':'VXO_MIX','R17':'VXO_MIX','VR2':'VXO_MIX','C25':'VXO_MIX',
    'L4':'PSN_AF','L5':'PSN_AF','IC2':'PSN_AF','Q8':'PSN_AF','Q14':'PSN_AF',
    'C11':'PSN_AF','C12':'PSN_AF','C13':'PSN_AF','C14':'PSN_AF',
    'C20':'PSN_AF','C29':'PSN_AF','R3':'PSN_AF','R4':'PSN_AF',
    'R5':'PSN_AF','R6':'PSN_AF','R36':'PSN_AF',
    'C100':'PSN_AF','C101':'PSN_AF',
    'Q5':'TX_CHAIN','D7':'TX_CHAIN','D8':'TX_CHAIN','Q15':'TX_CHAIN',
    'C32':'TX_CHAIN','R38':'TX_CHAIN','R40':'TX_CHAIN',
    'R41':'TX_CHAIN','R44':'TX_CHAIN','R34':'TX_CHAIN','R35':'TX_CHAIN',
    'R51':'TX_CHAIN','R52':'TX_CHAIN',
    'C4':'TX_CHAIN','C6':'TX_CHAIN','C7':'TX_CHAIN',
    'C102':'TX_CHAIN','C103':'TX_CHAIN','C104':'TX_CHAIN',
    'VR4':'TX_CHAIN','VR5':'TX_CHAIN',
    'Q2':'RX_CHAIN','Q3':'RX_CHAIN','Q4':'RX_CHAIN','Q6':'RX_CHAIN',
    'Q11':'RX_CHAIN','Q12':'RX_CHAIN','Q13':'RX_CHAIN','Q17':'RX_CHAIN',
    'T1':'RX_CHAIN',
    'R7':'RX_CHAIN','R8':'RX_CHAIN','R9':'RX_CHAIN','R10':'RX_CHAIN',
    'R11':'RX_CHAIN','R12':'RX_CHAIN','R13':'RX_CHAIN','R15':'RX_CHAIN',
    'R18':'RX_CHAIN','R20':'RX_CHAIN','R21':'RX_CHAIN','R22':'RX_CHAIN',
    'R23':'RX_CHAIN','R24':'RX_CHAIN','R25':'RX_CHAIN','R26':'RX_CHAIN',
    'R27':'RX_CHAIN','R28':'RX_CHAIN','R29':'RX_CHAIN','R30':'RX_CHAIN',
    'VR3':'RX_CHAIN','MIC1':'RX_CHAIN','LED1':'RX_CHAIN','LED2':'RX_CHAIN',
    **{f'C{n}':'RX_CHAIN' for n in range(158,168)},
    'C28':'RX_CHAIN','C30':'RX_CHAIN',
    'IC1':'POWER','J1':'POWER','L8':'POWER','L9':'POWER','L10':'POWER',
    'C5':'POWER','C8':'POWER','C8b1':'POWER',
    **{f'C{n}':'POWER' for n in range(105,127)},
    'R14':'POWER','R17':'POWER','R31':'POWER','R32':'POWER','R33':'POWER',
    'R42':'POWER','R43':'POWER',
    'VR1':'RF_AMP',
}

# ── Footprint body sizes (w, h mm) ───────────────────────────────────────────
FP_W = {
    'PSN_TRX:L_FCZ07S_CT':                    (9.2, 9.2),
    'PSN_TRX:Transformer_ST71_CB19':           (22, 20),
    'PSN_TRX:L_T50_2pin_Vertical':             (10, 14),
    'PSN_TRX:L_T30_2pin_Vertical':             ( 8,  9),
    'PSN_TRX:L_T30_3pin_Vertical':             ( 8,  9),
    'PSN_TRX:L_AL0510-153K_Vertical':          ( 5,  5),
    'PSN_TRX:C_Trimmer_TMCV01':                ( 8,  7),
    'Relay_THT:Relay_DPDT_Omron_G5V-2':        (16, 12),
    'Package_TO_SOT_THT:TO-72-4':              ( 6,  6),
    'Package_TO_SOT_THT:TO-92_Inline':         ( 4,  5),
    'Package_DIP:DIP-8_W7.62mm':               (10,  8),
    'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical': (4, 4),
    'Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm': (4, 4),
    'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm': (5, 5),
    'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm': ( 6,  6),
    'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm': ( 8,  8),
    'Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp': (4, 4),
    'LED_THT:LED_D3.0mm':                      ( 4,  4),
    'Crystal:Crystal_HC49-4H_Vertical':        ( 7,  7),
    'Potentiometer_THT:Potentiometer_Alps_RK09K_Single_Vertical': (10, 12),
    'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical': ( 4,  4),
    'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical': ( 7,  4),
    'Button_Switch_THT:SW_DIP_SPSTx01_Slide_6.7x4.1mm_W7.62mm_P2.54mm_LowProfile': (10, 6),
    'Button_Switch_THT:SW_E-Switch_EG1271_SPDT': (9, 7),
    'MountingHole:MountingHole_3.2mm_M3':      ( 0,  0),
    '_default':                                 ( 5,  5),
}

def get_wh(fp_str):
    if fp_str in FP_W:
        return FP_W[fp_str]
    # Match by name only (strip library prefix for both key and query)
    fp_name = fp_str.split(':')[-1] if ':' in fp_str else fp_str
    for k, v in FP_W.items():
        if k == '_default':
            continue
        k_name = k.split(':')[-1] if ':' in k else k
        if k_name == fp_name or k in fp_str:
            return v
    return FP_W['_default']


# Test/adjustment points that should be placed toward the front (lower y) of each block
# for easy oscilloscope probe access
PROBE_PRIORITY = {
    'TC1','TC2','TC3',           # trimmer caps – need screwdriver + probe access
    'X1',                         # VXO crystal (key frequency reference point)
    'Q1',                         # RF amp – main alignment point
    'Q7',                         # VXO buffer output
    'L4','L5',                    # PSN coils – key nodes
    'D1','D2','D3','D4',          # mixer diodes – balance adjustment
    'IC2',                        # op-amp – signal level check
    'T1',                         # audio transformer – AF level
    'Q5',                         # TX driver – output power
}


def sort_key(ref, w, h):
    """Large first; probe-priority items placed early (top of block, accessible)."""
    probe = -100 if ref in PROBE_PRIORITY else 0
    return probe - w * h   # negative = placed first


GAP = 1.2   # minimum gap between components (mm)


def place_even(board, refs, fp_map, area):
    """
    Shelf-packing placement:
    1. Sort: probe-priority (test-accessible) first, then by size
    2. Pack components left-to-right into shelves (rows)
    3. Spread shelves vertically to fill block height
    4. Spread components horizontally within each shelf
    Returns list of overflows (components that didn't fit).
    """
    x1, y1, x2, y2 = area
    W, H = x2 - x1, y2 - y1

    items = []
    for ref in refs:
        fp = board.FindFootprintByReference(ref)
        if fp is None:
            continue
        w, h = get_wh(fp_map.get(ref, '_default'))
        if w == 0:
            continue
        items.append((ref, w, h))

    # Probe-priority first, then large-first within each priority
    items.sort(key=lambda x: sort_key(x[0], x[1], x[2]))

    if not items:
        return []

    # ── Build shelves (left-to-right, greedy) ─────────────────────────────
    shelves   = []   # list of [(ref, w, h), ...]
    sh_heights = []  # max height of each shelf

    cur_shelf  = []
    cur_w_used = 0
    cur_h      = 0

    for ref, w, h in items:
        need_w = w + GAP
        if cur_shelf and cur_w_used + need_w > W + GAP:  # +GAP to allow trailing gap
            shelves.append(cur_shelf)
            sh_heights.append(cur_h + GAP)
            cur_shelf  = []
            cur_w_used = 0
            cur_h      = 0
        cur_shelf.append((ref, w, h))
        cur_w_used += need_w
        cur_h = max(cur_h, h)

    if cur_shelf:
        shelves.append(cur_shelf)
        sh_heights.append(cur_h + GAP)

    # ── Check total height fits ────────────────────────────────────────────
    total_h = sum(sh_heights)
    overflows = []
    if total_h > H + GAP:
        # Too tall: trim shelves from the bottom until they fit
        while total_h > H + GAP and shelves:
            removed_shelf = shelves.pop()
            removed_h     = sh_heights.pop()
            total_h      -= removed_h
            overflows.extend(r for r, w, h in removed_shelf)

    if not shelves:
        return overflows

    n_shelves = len(shelves)
    # Vertical spread: distribute shelves evenly
    v_extra = (H - total_h) / max(n_shelves, 1)
    v_extra = max(0, v_extra)   # clamp

    # ── Place components ───────────────────────────────────────────────────
    cy = y1 + GAP / 2
    for shelf, sh_h in zip(shelves, sh_heights):
        shelf_component_w = sum(w + GAP for _, w, h in shelf)
        h_extra = max(0, (W - shelf_component_w) / max(len(shelf) + 1, 1))

        cx = x1 + h_extra
        for ref, w, h in shelf:
            fp_obj = board.FindFootprintByReference(ref)
            if fp_obj:
                fp_obj.SetPosition(pcbnew.VECTOR2I(
                    mm(cx + w / 2),
                    mm(cy + (sh_h - GAP) / 2)
                ))
                fp_obj.SetOrientationDegrees(0)
            cx += w + GAP + h_extra

        cy += sh_h + v_extra

    return overflows


def main():
    print(f'Loading {PCB_FILE}')
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    fp_map = {fp.GetReference(): fp.GetFPIDAsString()
              for fp in board.GetFootprints()}

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

    print('\n  Block          comps  placed  overflow')
    print('  ' + '─' * 40)
    all_overflows = []
    for blk, area in BLOCKS.items():
        refs = block_refs[blk]
        if not refs:
            continue
        ov = place_even(board, refs, fp_map, area)
        placed = len(refs) - len(ov)
        all_overflows.extend(ov)
        print(f'  {blk:13s}  {len(refs):4d}   {placed:4d}   {len(ov):3d}')

    # Place overflows and unassigned below board for manual adjustment
    below = all_overflows + unassigned
    for i, ref in enumerate(below):
        fp = board.FindFootprintByReference(ref)
        if fp is None: continue
        fp.SetPosition(pcbnew.VECTOR2I(mm(5 + (i%25)*6), mm(103 + (i//25)*6)))

    board.Save(str(PCB_FILE))
    print(f'\nSaved: {PCB_FILE}')
    if below:
        print(f'Below-board ({len(below)}): {sorted(below)}')


if __name__ == '__main__':
    main()
