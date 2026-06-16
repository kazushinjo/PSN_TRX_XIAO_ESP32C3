import re
import uuid
import math

with open("PSN_TRX.kicad_sch", "r", encoding="utf-8") as f:
    content = f.read()

def world_pos(cx, cy, rot_deg, lx, ly):
    """Pin local → world coords using KiCad CCW rotation in Y-down coords."""
    r = math.radians(rot_deg)
    wx = cx + lx * math.cos(r) - ly * math.sin(r)
    wy = cy + lx * math.sin(r) + ly * math.cos(r)
    return round(wx, 4), round(wy, 4)

def make_nc(x, y):
    return f'\t(no_connect\n\t\t(at {x} {y})\n\t\t(uuid "{uuid.uuid4()}")\n\t)'

# ── 1. K1 (Relay:G5V-2) at (80.01, 77.47), rotation=270°
# All 8 pins: numbers and local coords from lib_symbols
k1_cx, k1_cy, k1_rot = 80.01, 77.47, 270
k1_pins = {
    '1':  (-10.16,  7.62),
    '4':  (  0.00, -7.62),
    '6':  ( -2.54,  7.62),
    '8':  (  2.54,  7.62),
    '9':  ( 12.70,  7.62),
    '11': (  7.62,  7.62),
    '13': ( 10.16, -7.62),
    '16': (-10.16, -7.62),
}

# ── 2. L1 (PSN_TRX:L_7T50_CT) at (129.54, 80.01), rotation=0°, pin 2
l1_cx, l1_cy, l1_rot = 129.54, 80.01, 0
l1_pin2 = (10.16, 0.0)

# ── 3. L2 (PSN_TRX:L_7T50_CT) at (218.44, 76.2), rotation=0°, pin 2
l2_cx, l2_cy, l2_rot = 218.44, 76.2, 0
l2_pin2 = (10.16, 0.0)

# ── 4. J1 (Conn_01x02) at (740, 20), rotation=0°, pins 1 and 2
j1_cx, j1_cy, j1_rot = 740.0, 20.0, 0
j1_pins = {
    '1': (-5.08,  0.00),
    '2': (-5.08, -2.54),
}

# Build list of no_connect entries to add
nc_entries = []

for pin_num, (lx, ly) in k1_pins.items():
    wx, wy = world_pos(k1_cx, k1_cy, k1_rot, lx, ly)
    nc_entries.append((wx, wy, f'K1 pin {pin_num}'))

wx, wy = world_pos(l1_cx, l1_cy, l1_rot, *l1_pin2)
nc_entries.append((wx, wy, 'L1 pin 2 (CT)'))

wx, wy = world_pos(l2_cx, l2_cy, l2_rot, *l2_pin2)
nc_entries.append((wx, wy, 'L2 pin 2 (CT)'))

for pin_num, (lx, ly) in j1_pins.items():
    wx, wy = world_pos(j1_cx, j1_cy, j1_rot, lx, ly)
    nc_entries.append((wx, wy, f'J1 pin {pin_num}'))

print(f"No-connect markers to add: {len(nc_entries)}")
for wx, wy, desc in nc_entries:
    print(f"  {desc}: ({wx}, {wy})")

# Insert all no_connect entries before the last ')' of the schematic
# Find the last occurrence of no_connect block and insert after it,
# or insert before the final ')' closing the root kicad_sch
nc_block = "\n" + "\n".join(make_nc(x, y) for x, y, _ in nc_entries)

# Insert before the very last line (the closing paren of kicad_sch)
last_paren = content.rfind('\n)')
if last_paren == -1:
    print("ERROR: could not find end of schematic")
    exit(1)

content = content[:last_paren] + nc_block + content[last_paren:]

# ── 5. Delete floating labels: ANT, +9V, Net-(SW1-B)
labels_to_delete = ['ANT', r'\+9V', r'Net-\(SW1-B\)']
for pattern in labels_to_delete:
    # Match full label block: \t(label "..." ... \t)
    m = re.search(r'\n\t\(label \"' + pattern + r'\".*?\n\t\)', content, re.DOTALL)
    if m:
        name = re.search(r'\"([^\"]+)\"', m.group(0)).group(1)
        content = content[:m.start()] + content[m.end():]
        print(f"Deleted label: {name}")
    else:
        print(f"WARNING: label pattern {pattern} not found")

# Verify
print(f"\nTotal no_connect in file: {content.count('(no_connect')}")
for lbl in ['\"ANT\"', '\"+9V\"', '\"Net-(SW1-B)\"']:
    print(f"Label {lbl} remaining: {content.count(lbl)}")

with open("PSN_TRX.kicad_sch", "w", encoding="utf-8") as f:
    f.write(content)
print("File written.")
