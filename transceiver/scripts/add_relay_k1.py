#!/usr/bin/env python3
"""
Add K1 (Omron G5V-2 DPDT relay) to PSN_TRX.kicad_sch.
- Removes SW2 and SW3 (replaced by K1)
- Places K1 near previous SW3 position
- Adds net labels to each pin for proper connections

Pin connections (deduced from netlist):
  Coil A1 (pin 1)  → Net-(SW1-B)  [TX control via SW1]
  Coil A2 (pin 16) → GND
  COM1   (pin 4)   → /ANT          [antenna common]
  NC1    (pin 6)   → Net-(L1-SA)   [RX path → L1 coil]
  NO1    (pin 8)   → Net-(SW3-C)   [TX path ← L15 output]
  COM2   (pin 13)  → +9V           [power common]
  NC2    (pin 11)  → Net-(L12-SB)  [RX bias supply]
  NO2    (pin 9)   → Net-(SW1-B)   [TX bias]
"""

import re
import shutil
import uuid
from pathlib import Path

SCH       = Path('PSN_TRX.kicad_sch')
RELAY_LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Relay.kicad_sym')
ROOT_UUID = '50835569-93ad-4c8c-aafc-424a6a3761ef'

# K1 placement position (schematic coordinates)
K1_X, K1_Y = 88.9, 95.0   # between former SW3 (77.47) and SW2 (118.11)


def uid():
    return str(uuid.uuid4())


def extract_lib_symbol(lib_path, sym_name):
    """Extract a (symbol "name" ...) block from a .kicad_sym file."""
    text = lib_path.read_text(encoding='utf-8')
    start = text.find(f'(symbol "{sym_name}"')
    if start == -1:
        raise ValueError(f'"{sym_name}" not found in {lib_path}')
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    raise ValueError('unclosed symbol')


def find_lib_end(content):
    """Return index of closing ) of (lib_symbols ...)."""
    start = content.find('\n\t(lib_symbols\n')
    depth = 0
    for i in range(start + 1, len(content)):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    raise ValueError('lib_symbols not closed')


def remove_symbol(content, ref):
    """Remove a symbol instance block by reference."""
    for m in re.finditer(r'\n\t\(symbol\n[\s\S]+?\n\t\)', content):
        if f'(property "Reference" "{ref}"' in m.group(0):
            content = content[:m.start()] + content[m.end():]
            return content, True
    return content, False


EFFECTS = '''\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)'''


def make_label(text, x, y, angle=0):
    """Create a (label ...) element matching KiCad schematic format."""
    return f'''
\t(label "{text}"
\t\t(at {x:.3f} {y:.3f} {angle})
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left)
\t\t)
\t\t(uuid "{uid()}")
\t)'''


def make_power_flag(net, x, y):
    """Create a power symbol connection (like +9V or GND)."""
    # Use a label for simplicity
    return make_label(net, x, y)


def make_k1_symbol(x, y):
    """Generate the K1 (G5V-2) symbol instance block."""
    # G5V-2 KiCad symbol is a single-unit symbol (unit 1)
    # Pin positions (relative to symbol center at 0,0 in the symbol coordinate space):
    # These come from the KiCad library symbol graphics
    # The symbol is placed at (x, y) in schematic coords
    return f'''
\t(symbol
\t\t(lib_id "Relay:G5V-2")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{uid()}")
\t\t(property "Reference" "K1"
\t\t\t(at {x + 16.51} {y - 3.81} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Value" "G5V-2"
\t\t\t(at {x + 16.51} {y - 1.27} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Footprint" "Relay_THT:Relay_DPDT_Omron_G5V-2"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Datasheet" "http://omronfs.omron.com/en_US/ecb/products/pdf/en-g5v_2.pdf"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(property "Description" "Relay Miniature Omron DPDT, TX/RX switch"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
{EFFECTS}
\t\t)
\t\t(pin "1"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "4"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "6"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "8"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "9"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "11"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "13"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pin "16"
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(instances
\t\t\t(project "PSN_TRX"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "K1")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def main():
    shutil.copy(SCH, SCH.with_suffix('.kicad_sch.pre_relay'))
    content = SCH.read_text(encoding='utf-8')

    # 1. Add Relay:G5V-2 to lib_symbols if not present
    if '"Relay:G5V-2"' not in content:
        g5v2_raw = extract_lib_symbol(RELAY_LIB, 'G5V-2')
        # Add "Relay:" prefix to top-level symbol only (first occurrence)
        g5v2_entry = g5v2_raw.replace('(symbol "G5V-2"', '(symbol "Relay:G5V-2"', 1)
        # Indent: first line gets +2 tabs (→ 2 tabs), subsequent get +1 tab
        # Original: 0-tab symbol opening, 2-tab children
        # Target:   2-tab symbol opening, 3-tab children
        lines = g5v2_entry.split('\n')
        indented = ['\t\t' + lines[0]]
        for line in lines[1:]:
            indented.append(('\t' + line) if line else '')
        g5v2_entry = '\n'.join(indented).rstrip()
        ls_end = find_lib_end(content)
        content = content[:ls_end] + '\n' + g5v2_entry + '\n\t' + content[ls_end:]
        print('Added Relay:G5V-2 to lib_symbols')
    else:
        print('Relay:G5V-2 already in lib_symbols')

    # 2. Remove SW2 and SW3
    for ref in ['SW2', 'SW3']:
        content, removed = remove_symbol(content, ref)
        print(f'{"Removed" if removed else "NOT found"}: {ref}')

    # 3. Add K1 symbol
    k1_block = make_k1_symbol(K1_X, K1_Y)

    # 4. Add net labels near K1 pins
    # G5V-2 pin offsets from center (based on KiCad symbol layout, unit=mm in schematic)
    # Left side (coil): A1(pin1) at x-15.24, A2(pin16) at x-15.24
    # Right side (contacts): COM1(4), NC1(6), NO1(8), COM2(13), NC2(11), NO2(9)
    # These are approximate positions based on the KiCad G5V-2 symbol geometry
    lx = K1_X - 15.24   # left side x (coil pins)
    rx = K1_X + 15.24   # right side x (contact pins)

    labels = [
        # (net_name, x, y)  — placed at pin endpoints
        ('Net-(SW1-B)',  lx - 2.54, K1_Y - 5.08),   # A1 (coil+) → TX control
        ('GND',          lx - 2.54, K1_Y + 5.08),   # A2 (coil-)
        ('/ANT',         rx + 2.54, K1_Y - 5.08),   # COM1 → antenna
        ('Net-(L1-SA)',  rx + 2.54, K1_Y + 5.08),   # NC1 → RX L1
        ('Net-(SW3-C)',  rx + 2.54, K1_Y - 2.54),   # NO1 → TX L15
        ('+9V',          lx - 2.54, K1_Y),           # COM2
        ('Net-(L12-SB)', rx + 2.54, K1_Y + 2.54),   # NC2 → RX bias
        ('Net-(SW1-B)',  rx + 2.54, K1_Y + 0),       # NO2 → TX bias
    ]
    label_blocks = ''.join(make_label(n, x, y) for n, x, y in labels)

    # Insert K1 + labels before final closing paren
    insert_pos = content.rfind('\n)')
    content = content[:insert_pos] + k1_block + label_blocks + content[insert_pos:]

    SCH.write_text(content, encoding='utf-8')
    print(f'\nSaved: {SCH}')
    print(f'K1 placed at ({K1_X}, {K1_Y})')
    print('''
Pin connections (verify in KiCad and adjust wires):
  Pin 1  (A1, coil+) → Net-(SW1-B)    TX control signal
  Pin 16 (A2, coil-) → GND
  Pin 4  (COM1)      → /ANT            Antenna common
  Pin 6  (NC1)       → Net-(L1-SA)    RX: antenna → L1
  Pin 8  (NO1)       → Net-(SW3-C)    TX: L15 output → antenna
  Pin 13 (COM2)      → +9V            Power common
  Pin 11 (NC2)       → Net-(L12-SB)   RX bias supply
  Pin 9  (NO2)       → Net-(SW1-B)    TX bias
''')


if __name__ == '__main__':
    main()
