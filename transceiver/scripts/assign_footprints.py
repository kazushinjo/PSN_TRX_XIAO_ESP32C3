#!/usr/bin/env python3
"""Assign footprints to all unassigned components in PSN_TRX.kicad_sch."""

import re
import shutil
from pathlib import Path

SCH = Path('PSN_TRX.kicad_sch')

# Reference -> footprint mapping
FP = {
    # --- Capacitors: small ceramic disc (pF range) ---
    **{r: 'Capacitor_THT:C_Disc_D3.0mm_W1.6mm_P2.50mm' for r in [
        'C1', 'C2', 'C9', 'C10', 'C11', 'C12', 'C13', 'C14',
        'C17', 'C18', 'C19', 'C23', 'C24', 'C25', 'C31', 'C32',
    ]},
    # --- Capacitors: larger ceramic disc (1nF / 10nF / 100nF) ---
    **{r: 'Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P2.50mm' for r in [
        'C3', 'C4', 'C6', 'C7', 'C20', 'C29',
        *[f'C{n}' for n in [
            100, 101, 102, 103, 104, 105,
            111, 112, 113, 114, 115, 116, 117, 118,
            119, 120, 121, 122, 123, 124, 125, 126,
        ]],
    ]},
    # --- Electrolytic 1uF ---
    **{f'C{n}': 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm' for n in
        [158, 159, 160, 161, 162, 163, 164, 165, 166, 167]},
    # --- Electrolytic 10uF ---
    **{r: 'Capacitor_THT:CP_Radial_D5.0mm_P2.00mm' for r in ['C5', 'C8', 'C8b1']},
    # --- Electrolytic 100uF ---
    **{r: 'Capacitor_THT:CP_Radial_D6.3mm_P2.50mm' for r in ['C28', 'C30']},

    # --- Transistors TO-92 ---
    **{r: 'Package_TO_SOT_THT:TO-92_Inline' for r in [
        'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8',
        'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15', 'Q17',
    ]},
    # --- 3SK59: 4-lead metal can TO-72 ---
    'Q1': 'Package_TO_SOT_THT:TO-72-4',

    # --- ICs ---
    'IC1': 'Package_TO_SOT_THT:TO-92_Inline',   # LP2950L-5.0V (TO-92)
    'IC2': 'Package_DIP:DIP-8_W7.62mm',          # NJM2904 (DIP-8)

    # --- LEDs ---
    'LED1': 'LED_THT:LED_D3.0mm',
    'LED2': 'LED_THT:LED_D3.0mm',

    # --- Crystal (HC-49 vertical) ---
    'X1': 'Crystal:Crystal_HC49-4H_Vertical',

    # --- Switches ---
    'SW1': 'Button_Switch_THT:SW_DIP_SPSTx01_Slide_6.7x4.1mm_W7.62mm_P2.54mm_LowProfile',
    'SW2': 'Button_Switch_THT:SW_E-Switch_EG1271_SPDT',
    'SW3': 'Button_Switch_THT:SW_E-Switch_EG1271_SPDT',

    # --- Potentiometers (VR1/VR2 は on_board no のため除外) ---
    **{r: 'PSN_TRX:Potentiometer_TOCOS_GF063P_Vertical' for r in
        ['VR3', 'VR4', 'VR5', 'VR6', 'VR7']},

    # --- Microphone (pin header connector) ---
    'MIC1': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',

    # --- 1mH axial inductors (vertical, same style as L8) ---
    'L9':  'PSN_TRX:L_AL0510-153K_Vertical',
    'L10': 'PSN_TRX:L_AL0510-153K_Vertical',

    # --- T-30-10 toroids (custom, vertical mount) ---
    'L4': 'PSN_TRX:L_T30_2pin_Vertical',
    'L5': 'PSN_TRX:L_T30_3pin_Vertical',

    # --- T-50-10 toroids (custom, vertical mount) ---
    'L14': 'PSN_TRX:L_T50_2pin_Vertical',
    'L15': 'PSN_TRX:L_T50_2pin_Vertical',
}


def update_footprints(content: str, fp_map: dict) -> tuple[str, list]:
    """Update Footprint properties in KiCad schematic content.

    Returns (updated_content, list_of_updated_refs).
    """
    # Find where lib_symbols section ends so we only process instance symbols
    lib_start = content.find('\n\t(lib_symbols\n')
    lib_end = lib_start + 1
    depth = 0
    for i in range(lib_start + 1, len(content)):
        c = content[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                lib_end = i + 1
                break

    pre = content[:lib_end]
    post = content[lib_end:]

    # Split post into segments at each top-level (symbol ...) block
    # Top-level instances: \n\t(symbol\n  (no quoted name after "symbol")
    split_re = re.compile(r'(?=\n\t\(symbol\n)')
    segments = split_re.split(post)

    updated_refs = []
    result_segs = []

    for seg in segments:
        ref_m = re.search(r'\t\t\(property "Reference" "([^"]+)"', seg)
        if ref_m:
            ref = ref_m.group(1)
            if ref in fp_map:
                new_fp = fp_map[ref]
                new_seg = re.sub(
                    r'\t\t\(property "Footprint" "[^"]*"',
                    f'\t\t(property "Footprint" "{new_fp}"',
                    seg,
                )
                if new_seg != seg:
                    updated_refs.append(ref)
                seg = new_seg
        result_segs.append(seg)

    return pre + ''.join(result_segs), updated_refs


def main():
    if not SCH.exists():
        print(f'ERROR: {SCH} not found. Run from the project directory.')
        return

    bak = SCH.with_suffix('.kicad_sch.bak')
    shutil.copy(SCH, bak)
    print(f'Backup: {bak}')

    content = SCH.read_text(encoding='utf-8')
    new_content, updated = update_footprints(content, FP)

    SCH.write_text(new_content, encoding='utf-8')

    print(f'\nUpdated {len(updated)}/{len(FP)} footprints:')
    for ref in sorted(updated):
        print(f'  {ref:8s} -> {FP[ref]}')

    missing = [r for r in FP if r not in updated]
    if missing:
        print(f'\nNot found in schematic ({len(missing)}): {", ".join(sorted(missing))}')

    # Count remaining empty footprints (excluding power/flag symbols)
    remaining = re.findall(
        r'\t\t\(property "Reference" "([^#][^"]+)"\s*\n'
        r'(?:(?!\t\t\(property "Footprint")[\s\S])*?'
        r'\t\t\(property "Footprint" ""',
        new_content,
    )
    if remaining:
        print(f'\nStill empty footprints: {sorted(set(remaining))}')
    else:
        print('\nAll non-power footprints assigned.')


if __name__ == '__main__':
    main()

