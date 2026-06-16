#!/usr/bin/env python3
"""
add_l4_l5.py
VXO部 L4・L5 部品シンボルを既存の PSN_TRX.kicad_sch に追加する。
配線は KiCad で手動実施。

L4: T-30-10, 0.6mmホルマル線 6回 (Device:L, 単巻)
L5: T-30-10, 0.4mmホルマル線 6回 + リンク巻き線 1回 (Device:Transformer_1P_1S)
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
# ============================================================
# L4: T-30-10, 0.6mmホルマル線 6回 (単巻インダクタ)
#   位置: VXOブロック内 (645.16, 360.68) = 254×2.54, 142×2.54
L4 = component(
    "L4", "T-30-10 6T/0.4mm",
    "Device:L",
    645.16, 360.68,
    desc="T-30-10 0.4mmホルマル線6回"
)

# L5: T-30-10, 0.4mmホルマル線 6回 + リンク巻き線 1回 (トランス, 1P1S)
#   位置: L4の左隣 (617.22, 360.68) = 243×2.54, 142×2.54
L5 = component(
    "L5", "T-30-10 6T+1T/0.4mm",
    "Device:Transformer_1P_1S",
    617.22, 360.68,
    desc="T-30-10 0.4mmホルマル線6回+リンク1回"
)

adds = [L4, L5]

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
    print("  L4: Device:L  T-30-10 6T/0.4mm  at (645.16, 360.68)")
    print("  L5: Device:Transformer_1P_1S  T-30-10 6T+1T/0.4mm  at (617.22, 360.68)")
    print()
    print("※ 配線は KiCad で手動追加してください")

if __name__ == "__main__":
    main()
