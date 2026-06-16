"""
FCZ 07S（サトー電気 7T-50シリーズ）フットプリント作成スクリプト
寸法: A=7.2mm B=4.5mm C=1.0mm(穴径) D=0.7mm(リード径) E=15.3mm F=12.0mm

ピン配置（トップビュー、基板上面から）:
  右列(Secondary+CT): Pin1(SA) y=+2.25, Pin2(CT) y=0, Pin3(SB) y=-2.25  x=+2.25
  左列(Primary):      Pin4(AA) y=+2.25, Pin5(AB) y=-2.25                  x=-2.25
"""

MOD_PATH = r"C:\Users\kazus\KiCad\PSN_TRX_New\PSN_TRX.pretty\L_FCZ07S_CT.kicad_mod"

# 寸法
A = 7.2    # ボディ幅
B = 4.5    # ピン間距離（行・列の基準）
C = 1.0    # ドリル穴径
PAD = 1.7  # パッド径

HALF = B / 2   # 2.25mm

# ピン定義: (番号, x, y, name)
PINS = [
    (1,  HALF,  HALF, "SA"),
    (2,  HALF,  0,    "CT"),
    (3,  HALF, -HALF, "SB"),
    (4, -HALF,  HALF, "AA"),
    (5, -HALF, -HALF, "AB"),
]

def pad(num, x, y, drill, size, name=""):
    shape = "circle"
    layers = '"*.Cu" "*.Mask"'
    attr = ""
    if num == 1:
        shape = "rect"  # ピン1は四角パッド
    return f"""
    (pad "{num}" thru_hole {shape}
      (at {x} {y})
      (size {size} {size})
      (drill {drill})
      (layers {layers})
    )"""

lines = []
lines.append('(footprint "L_FCZ07S_CT"')
lines.append('  (version 20241209)')
lines.append('  (generator kicad_pcbnew)')
lines.append('  (layer "F.Cu")')
lines.append('  (descr "Sato Denki FCZ 07S centre-tap transformer 7T-50 series")')
lines.append('  (tags "coil transformer FCZ 7T 07S centre-tap ham")')

# リファレンスとバリュー
lines.append('  (property "Reference" "REF**"')
lines.append('    (at 0 -5.0 0)')
lines.append('    (layer "F.SilkS")')
lines.append('    (effects (font (size 1.0 1.0)))')
lines.append('  )')
lines.append('  (property "Value" "L_FCZ07S_CT"')
lines.append('    (at 0 5.0 0)')
lines.append('    (layer "F.Fab")')
lines.append('    (effects (font (size 1.0 1.0)))')
lines.append('  )')

# ボディ輪郭（Fab層）: A×A 正方形
half_a = A / 2
lines.append(f'  (fp_rect')
lines.append(f'    (start -{half_a} -{half_a})')
lines.append(f'    (end {half_a} {half_a})')
lines.append(f'    (layer "F.Fab")')
lines.append(f'    (stroke (width 0.1) (type solid))')
lines.append(f'  )')

# シルク: ピン1マーク
lines.append(f'  (fp_circle')
lines.append(f'    (center {HALF} {HALF+1.0})')
lines.append(f'    (end {HALF+0.3} {HALF+1.0})')
lines.append(f'    (layer "F.SilkS")')
lines.append(f'    (stroke (width 0.12) (type solid))')
lines.append(f'    (fill solid)')
lines.append(f'  )')

# コートヤード: A+0.5mm マージン
margin = 0.5
lines.append(f'  (fp_rect')
lines.append(f'    (start -{half_a+margin} -{half_a+margin})')
lines.append(f'    (end {half_a+margin} {half_a+margin})')
lines.append(f'    (layer "B.CrtYd")')
lines.append(f'    (stroke (width 0.05) (type solid))')
lines.append(f'  )')
lines.append(f'  (fp_rect')
lines.append(f'    (start -{half_a+margin} -{half_a+margin})')
lines.append(f'    (end {half_a+margin} {half_a+margin})')
lines.append(f'    (layer "F.CrtYd")')
lines.append(f'    (stroke (width 0.05) (type solid))')
lines.append(f'  )')

# スルーホールパッド
for num, x, y, name in PINS:
    shape = "rect" if num == 1 else "circle"
    lines.append(f'  (pad "{num}" thru_hole {shape}')
    lines.append(f'    (at {x} {y})')
    lines.append(f'    (size {PAD} {PAD})')
    lines.append(f'    (drill {C})')
    lines.append(f'    (layers "*.Cu" "*.Mask")')
    lines.append(f'    (net_name "{name}")')
    lines.append(f'  )')

lines.append(')')

with open(MOD_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"フットプリント作成: {MOD_PATH}")
print(f"ピン配置:")
for num, x, y, name in PINS:
    print(f"  Pin{num} ({name}): ({x:+.2f}, {y:+.2f})")
print(f"ボディ: {A}x{A}mm, 穴径: {C}mm, パッド径: {PAD}mm")
