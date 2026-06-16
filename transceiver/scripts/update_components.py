#!/usr/bin/env python3
"""
Update component footprints and add power connector J1 to PSN_TRX.kicad_sch.

Changes:
  VR1, VR2        -> 3-pin header (panel mount, direct wire)
  LED1, LED2      -> 2-pin header (panel mount, direct wire)
  Add J1 (J_PWR)  -> 2-pin header for DC power input
  SW2             -> footprint = G5V-2 (symbol change still needed in KiCad GUI)
  SW3             -> DNP (merged into K1/G5V-2 DPDT)

NOTE: K1 (G5V-2 relay) must be added manually in KiCad schematic editor:
  - Delete SW2, SW3 symbols
  - Add Relay:G5V-2 as K1, footprint Relay_THT:Relay_DPDT_Omron_G5V-2
  - Reconnect TX/RX control lines to coil (A1, A2) and antenna/signal paths to contacts
"""

import re
import shutil
import uuid
from pathlib import Path

SCH = Path('PSN_TRX.kicad_sch')
ROOT_UUID = '50835569-93ad-4c8c-aafc-424a6a3761ef'

# ── footprint updates for existing components ─────────────────────────────────
FP_UPDATES = {
    'VR1':  'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'VR2':  'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
    'LED1': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
    'LED2': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
}


def update_footprints(content: str, fp_map: dict) -> tuple[str, list]:
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

    split_re = re.compile(r'(?=\n\t\(symbol\n)')
    segments = split_re.split(post)

    updated = []
    result_segs = []
    for seg in segments:
        ref_m = re.search(r'\t\t\(property "Reference" "([^"]+)"', seg)
        if ref_m:
            ref = ref_m.group(1)
            if ref in fp_map:
                new_seg = re.sub(
                    r'\t\t\(property "Footprint" "[^"]*"',
                    f'\t\t(property "Footprint" "{fp_map[ref]}"',
                    seg,
                )
                if new_seg != seg:
                    updated.append(ref)
                seg = new_seg
        result_segs.append(seg)

    return pre + ''.join(result_segs), updated


# ── J1 power connector symbol block ──────────────────────────────────────────
J1_SYMBOL = '''\n\t(symbol
\t\t(lib_id "Connector_Generic:Conn_01x02")
\t\t(at 740 20 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{sym_uuid}")
\t\t(property "Reference" "J1"
\t\t\t(at 740 16 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "PWR_IN"
\t\t\t(at 745 16 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical"
\t\t\t(at 740 20 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at 740 20 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "DC power input, 2-pin header, Pin1=+9V, Pin2=GND"
\t\t\t(at 740 20 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{pin1_uuid}")
\t\t)
\t\t(pin "2"
\t\t\t(uuid "{pin2_uuid}")
\t\t)
\t\t(instances
\t\t\t(project "PSN_TRX"
\t\t\t\t(path "/{root_uuid}"
\t\t\t\t\t(reference "J1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def add_j1(content: str) -> str:
    """Append J1 power connector before the closing paren of the schematic."""
    sym_uuid  = str(uuid.uuid4())
    pin1_uuid = str(uuid.uuid4())
    pin2_uuid = str(uuid.uuid4())
    block = J1_SYMBOL.format(
        sym_uuid=sym_uuid,
        pin1_uuid=pin1_uuid,
        pin2_uuid=pin2_uuid,
        root_uuid=ROOT_UUID,
    )
    # Insert before the final closing paren of the schematic
    insert_pos = content.rfind('\n)')
    return content[:insert_pos] + block + content[insert_pos:]


def main():
    bak = SCH.with_suffix('.kicad_sch.bak2')
    shutil.copy(SCH, bak)
    print(f'Backup: {bak}')

    content = SCH.read_text(encoding='utf-8')

    # 1. Update footprints
    content, updated = update_footprints(content, FP_UPDATES)
    print(f'\nFootprint updates ({len(updated)}):')
    for ref in updated:
        print(f'  {ref:6s} -> {FP_UPDATES[ref]}')

    # 2. Add J1 power connector
    if '"J1"' not in content:
        content = add_j1(content)
        print('\nAdded: J1 (PWR_IN, PinHeader_1x02, at 740,20)')
    else:
        print('\nJ1 already exists, skipped.')

    SCH.write_text(content, encoding='utf-8')
    print('\nDone. PSN_TRX.kicad_sch updated.')
    print('''
─────────────────────────────────────────────────────
MANUAL STEPS REQUIRED IN KiCad SCHEMATIC EDITOR:
─────────────────────────────────────────────────────
1. K1 (G5V-2 DPDT relay) — replaces SW2 + SW3:
   a. Delete SW2 and SW3 symbols
   b. Add symbol: Relay:G5V-2, Ref=K1
      Footprint: Relay_THT:Relay_DPDT_Omron_G5V-2
   c. Connect coil A1/A2 to TX/RX control signal
   d. Connect contacts to antenna/signal paths

2. J1 power connector:
   - Already added at schematic coord (740, 20)
   - Connect Pin1 to +9V net, Pin2 to GND net

3. VR1/VR2 (3-pin header — wire to panel pot):
   - Pin1=CW, Pin2=Wiper, Pin3=CCW  (confirm polarity)

4. LED1/LED2 (2-pin header — wire to panel LED):
   - Pin1=Anode, Pin2=Cathode
─────────────────────────────────────────────────────
''')


if __name__ == '__main__':
    main()
