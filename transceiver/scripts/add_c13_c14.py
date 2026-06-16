#!/usr/bin/env python3
"""
add_c13_c14.py
VXO部 C13・C14 (40pFトリマ) 部品シンボルを既存の PSN_TRX.kicad_sch に追加する。
配線は KiCad で手動実施。
"""

import uuid

INPUT_PATH  = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"
OUTPUT_PATH = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"

def gen_uuid():
    return str(uuid.uuid4())

def mm(v):
    return round(float(v), 4)

def component(ref, value, lib_sym, x, y, rot=0, desc=""):
    u = gen_uuid()
    lines = [
        f'  (symbol',
        f'    (lib_id "{lib_sym}")',
        f'    (at {mm(x)} {mm(y)} {rot})',
        f'    (unit 1)',
        f'    (exclude_from_sim no)',
        f'    (in_bom yes)',
        f'    (on_board yes)',
        f'    (dnp no)',
        f'    (fields_autoplaced yes)',
        f'    (uuid "{u}")',
        f'    (property "Reference" "{ref}"',
        f'      (at {mm(x)} {mm(y - 3.81)} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
        f'    (property "Value" "{value}"',
        f'      (at {mm(x)} {mm(y + 3.81)} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
        f'    (property "Footprint" ""',
        f'      (at {mm(x)} {mm(y)} 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes))',
        f'    )',
        f'    (property "Datasheet" ""',
        f'      (at {mm(x)} {mm(y)} 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes))',
        f'    )',
    ]
    if desc:
        lines += [
            f'    (property "ki_description" "{desc}"',
            f'      (at {mm(x)} {mm(y)} 0)',
            f'      (effects (font (size 1.27 1.27)) (hide yes))',
            f'    )',
        ]
    lines.append('  )')
    return "\n".join(lines)

# ============================================================
# VXO部 追加部品
# Q8 (VXO発振) at (614.68, 309.88), TC2 (5p) at (614.68, 248.92)
# ============================================================
# C13: 40pFトリマ  (635.00, 271.78) = 250×2.54, 107×2.54
C13 = component("C13", "40p", "Device:C", 635.00, 271.78, desc="VXOトリマ40p")

# C14: 40pFトリマ  (657.86, 271.78) = 259×2.54, 107×2.54
C14 = component("C14", "40p", "Device:C", 657.86, 271.78, desc="VXOトリマ40p")

adds = [C13, C14]

# ============================================================
# ファイル更新
# ============================================================
def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    last = content.rfind("\n)")
    if last == -1:
        last = content.rfind(")")
    if last == -1:
        print("ERROR: 末尾の ) が見つかりません")
        return

    insert = "\n" + "\n\n".join(adds) + "\n"
    new_content = content[:last] + insert + content[last:]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"完了: {OUTPUT_PATH}")
    print(f"ファイルサイズ: {len(new_content):,} bytes")
    print()
    print("追加部品:")
    print("  C13: Device:C  40p  at (635.00, 271.78)")
    print("  C14: Device:C  40p  at (657.86, 271.78)")
    print()
    print("※ 配線は KiCad で手動追加してください")

if __name__ == "__main__":
    main()
