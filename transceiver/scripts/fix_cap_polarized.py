import re

with open("PSN_TRX.kicad_sch", "r", encoding="utf-8") as f:
    content = f.read()

# ── 1. C_Polarized symbol definition for lib_symbols (2-tab indent) ──
new_sym = '\t\t(symbol "Device:C_Polarized"\n\t\t\t(pin_numbers\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t\t(pin_names\n\t\t\t\t(offset 0.254)\n\t\t\t)\n\t\t\t(exclude_from_sim no)\n\t\t\t(in_bom yes)\n\t\t\t(on_board yes)\n\t\t\t(in_pos_files yes)\n\t\t\t(duplicate_pin_numbers_are_jumpers no)\n\t\t\t(property "Reference" "C"\n\t\t\t\t(at 0.635 2.54 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t\t(justify left)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(property "Value" "C_Polarized"\n\t\t\t\t(at 0.635 -2.54 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t\t(justify left)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(property "Footprint" ""\n\t\t\t\t(at 0.9652 -3.81 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(hide yes)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(property "Datasheet" ""\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(hide yes)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(property "Description" "Polarized capacitor"\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(hide yes)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(property "ki_keywords" "cap capacitor"\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(hide yes)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(property "ki_fp_filters" "CP_*"\n\t\t\t\t(at 0 0 0)\n\t\t\t\t(show_name no)\n\t\t\t\t(do_not_autoplace no)\n\t\t\t\t(hide yes)\n\t\t\t\t(effects\n\t\t\t\t\t(font\n\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(symbol "C_Polarized_0_1"\n\t\t\t\t(rectangle\n\t\t\t\t\t(start -2.286 0.508)\n\t\t\t\t\t(end 2.286 1.016)\n\t\t\t\t\t(stroke\n\t\t\t\t\t\t(width 0)\n\t\t\t\t\t\t(type default)\n\t\t\t\t\t)\n\t\t\t\t\t(fill\n\t\t\t\t\t\t(type none)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t\t(polyline\n\t\t\t\t\t(pts\n\t\t\t\t\t\t(xy -1.778 2.286) (xy -0.762 2.286)\n\t\t\t\t\t)\n\t\t\t\t\t(stroke\n\t\t\t\t\t\t(width 0)\n\t\t\t\t\t\t(type default)\n\t\t\t\t\t)\n\t\t\t\t\t(fill\n\t\t\t\t\t\t(type none)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t\t(polyline\n\t\t\t\t\t(pts\n\t\t\t\t\t\t(xy -1.27 2.794) (xy -1.27 1.778)\n\t\t\t\t\t)\n\t\t\t\t\t(stroke\n\t\t\t\t\t\t(width 0)\n\t\t\t\t\t\t(type default)\n\t\t\t\t\t)\n\t\t\t\t\t(fill\n\t\t\t\t\t\t(type none)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t\t(rectangle\n\t\t\t\t\t(start 2.286 -0.508)\n\t\t\t\t\t(end -2.286 -1.016)\n\t\t\t\t\t(stroke\n\t\t\t\t\t\t(width 0)\n\t\t\t\t\t\t(type default)\n\t\t\t\t\t)\n\t\t\t\t\t(fill\n\t\t\t\t\t\t(type outline)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(symbol "C_Polarized_1_1"\n\t\t\t\t(pin passive line\n\t\t\t\t\t(at 0 3.81 270)\n\t\t\t\t\t(length 2.794)\n\t\t\t\t\t(name ""\n\t\t\t\t\t\t(effects\n\t\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t\t)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t\t(number "1"\n\t\t\t\t\t\t(effects\n\t\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t\t)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t\t(pin passive line\n\t\t\t\t\t(at 0 -3.81 90)\n\t\t\t\t\t(length 2.794)\n\t\t\t\t\t(name ""\n\t\t\t\t\t\t(effects\n\t\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t\t)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t\t(number "2"\n\t\t\t\t\t\t(effects\n\t\t\t\t\t\t\t(font\n\t\t\t\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t\t\t\t)\n\t\t\t\t\t\t)\n\t\t\t\t\t)\n\t\t\t\t)\n\t\t\t)\n\t\t\t(embedded_fonts no)\n\t\t)'

# ── 2. Insert C_Polarized after the Device:C symbol block in lib_symbols ──
pattern = r'\t\t\(symbol "Device:C".*?\n\t\t\)'
match = re.search(pattern, content, re.DOTALL)
if not match:
    print("ERROR: Device:C symbol block not found in lib_symbols!")
    exit(1)
print(f"Found Device:C symbol block at {match.start()}-{match.end()}")
print(f"  First 50: {repr(match.group()[:50])}")
print(f"  Last 30:  {repr(match.group()[-30:])}")

new_content = content[:match.end()] + '\n' + new_sym + content[match.end():]

# ── 3. Change lib_id for only C5, C8, C8b1 instances ──
count = 0
for ref in ['C5', 'C8', 'C8b1']:
    # Find the instance block: \t(symbol\n\t\t(lib_id "Device:C")\n
    # then find the one whose Reference matches ref
    idx = 0
    while True:
        pos = new_content.find('\n\t(symbol\n\t\t(lib_id "Device:C")\n', idx)
        if pos == -1:
            break
        chunk_end = new_content.find('\n\t)', pos + 5, pos + 3000)
        chunk = new_content[pos:chunk_end + 3]
        ref_m = re.search(r'\(property "Reference" "([^"]+)"', chunk)
        val_m = re.search(r'\(property "Value" "([^"]+)"', chunk)
        if ref_m and ref_m.group(1) == ref:
            # Replace lib_id in this block only
            old_lib = '\n\t(symbol\n\t\t(lib_id "Device:C")\n'
            new_lib = '\n\t(symbol\n\t\t(lib_id "Device:C_Polarized")\n'
            new_content = new_content[:pos] + new_lib + new_content[pos + len(old_lib):]
            print(f"Changed {ref} (val={val_m.group(1) if val_m else '?'}) from Device:C to Device:C_Polarized")
            count += 1
            break
        idx = pos + 1

print(f"\nTotal instances changed: {count}")
print(f"Device:C_Polarized lib_id count: {new_content.count('(lib_id \"Device:C_Polarized\")')}")
print(f"Device:C_Polarized symbol count: {new_content.count('(symbol \"Device:C_Polarized\"')}")

with open("PSN_TRX.kicad_sch", "w", encoding="utf-8") as f:
    f.write(new_content)
print("File written.")
