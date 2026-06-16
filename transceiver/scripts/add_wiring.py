#!/usr/bin/env python3
"""
PSN_TRX add_wiring.py
PSN_TRX.kicad_sch に電源シンボル・配線・ネットラベルを追加する

追加内容:
  1. バイパスコン全下端 → GND
  2. IC1 電源ピン (+9V入力 / +5V出力 / GND)
  3. 主な電源レール接続 (+9V, GND)
  4. R1/R14 バイアス (Q1 G2) 上下端
  5. R2/R21 バイアス (Q2) 上下端
  6. VR1/VR2 下端 → GND
  7. C25 上端 → +9V (VXO電源)
  8. ブロック間ネットラベル
  9. 主要ブロック内接続配線
"""

import uuid

INPUT_PATH  = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"
OUTPUT_PATH = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"

_pwr_n = [200]

def gen_uuid():
    return str(uuid.uuid4())

def mm(v):
    return round(float(v), 4)

# ============================================================
# 電源シンボル生成
# ============================================================
def _pwr(lib_id, val_str, x, y, ref_dy, val_dy):
    n = _pwr_n[0]; _pwr_n[0] += 1
    u = gen_uuid()
    return (
        f'  (symbol\n'
        f'    (lib_id "{lib_id}")\n'
        f'    (at {mm(x)} {mm(y)} 0)\n'
        f'    (unit 1)\n'
        f'    (exclude_from_sim no)\n'
        f'    (in_bom yes)\n'
        f'    (on_board yes)\n'
        f'    (dnp no)\n'
        f'    (uuid "{u}")\n'
        f'    (property "Reference" "#PWR{n:03d}"\n'
        f'      (at {mm(x)} {mm(y + ref_dy)} 0)\n'
        f'      (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'    (property "Value" "{val_str}"\n'
        f'      (at {mm(x)} {mm(y + val_dy)} 0)\n'
        f'      (effects (font (size 1.27 1.27)))\n'
        f'    )\n'
        f'    (property "Footprint" ""\n'
        f'      (at {mm(x)} {mm(y)} 0)\n'
        f'      (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'    (property "Datasheet" ""\n'
        f'      (at {mm(x)} {mm(y)} 0)\n'
        f'      (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'  )'
    )

def gnd(x, y):
    """GND: ピンが(x,y)、三角が下へ、"GND"テキストが下に表示"""
    return _pwr("power:GND", "GND", x, y, +6.35, +3.81)

def pwr9v(x, y):
    """+9V: ピンが(x,y)、矢印が上へ、"+9V"テキストが上に表示"""
    return _pwr("power:+9V", "+9V", x, y, +3.81, -3.556)

def pwr5v(x, y):
    return _pwr("power:+5V", "+5V", x, y, +3.81, -3.556)

# ============================================================
# ワイヤ生成
# ============================================================
def wire(x1, y1, x2, y2):
    u = gen_uuid()
    return (
        f'  (wire\n'
        f'    (pts\n'
        f'      (xy {mm(x1)} {mm(y1)}) (xy {mm(x2)} {mm(y2)})\n'
        f'    )\n'
        f'    (stroke (width 0) (type default))\n'
        f'    (uuid "{u}")\n'
        f'  )'
    )

# ============================================================
# ネットラベル生成
# ============================================================
def netlabel(name, x, y, angle=0):
    """局所ネットラベル (同シート内接続)"""
    u = gen_uuid()
    justify = "left" if angle in (0, 270) else "right"
    return (
        f'  (label "{name}"\n'
        f'    (at {mm(x)} {mm(y)} {angle})\n'
        f'    (fields_autoplaced yes)\n'
        f'    (effects (font (size 1.27 1.27)) (justify {justify}))\n'
        f'    (uuid "{u}")\n'
        f'  )'
    )

# ============================================================
# ピン座標ヘルパ (Y反転済み)
# x_sch = x_comp + px_sym
# y_sch = y_comp - py_sym
# ============================================================
def r_top(cx, cy):    return (cx, cy - 3.81)   # Device:R/C/L Pin1
def r_bot(cx, cy):    return (cx, cy + 3.81)   # Device:R/C/L Pin2
def vr_top(cx, cy):   return (cx, cy - 3.81)   # R_Potentiometer Pin1
def vr_wip(cx, cy):   return (cx + 3.81, cy)   # R_Potentiometer Pin2(wiper)
def vr_bot(cx, cy):   return (cx, cy + 3.81)   # R_Potentiometer Pin3
def npn_c(cx, cy):    return (cx + 2.54, cy - 5.08)   # Q_NPN_BCE C
def npn_b(cx, cy):    return (cx - 5.08, cy)          # Q_NPN_BCE B
def npn_e(cx, cy):    return (cx + 2.54, cy + 5.08)   # Q_NPN_BCE E
def jfet_d(cx, cy):   return (cx + 2.54, cy - 5.08)   # Q_NJFET_GDS D
def jfet_g(cx, cy):   return (cx - 5.08, cy)          # Q_NJFET_GDS G
def jfet_s(cx, cy):   return (cx + 2.54, cy + 5.08)   # Q_NJFET_GDS S
def sk263_d(cx, cy):  return (cx + 2.54, cy - 5.08)   # 3SK263 D
def sk263_g1(cx, cy): return (cx - 5.08, cy - 2.54)   # 3SK263 G1
def sk263_g2(cx, cy): return (cx - 5.08, cy + 2.54)   # 3SK263 G2
def sk263_s(cx, cy):  return (cx + 2.54, cy + 5.08)   # 3SK263 S
def tr_AA(cx, cy):    return (cx - 10.16, cy - 5.08)  # Transformer_1P_1S AA(一次上)
def tr_AB(cx, cy):    return (cx - 10.16, cy + 5.08)  # Transformer_1P_1S AB(一次下)
def tr_SA(cx, cy):    return (cx + 10.16, cy + 5.08)  # Transformer_1P_1S SA(二次下)
def tr_SB(cx, cy):    return (cx + 10.16, cy - 5.08)  # Transformer_1P_1S SB(二次上)
def ic1_vi(cx, cy):   return (cx - 7.62, cy)          # MC78L05 VI(入力)
def ic1_vo(cx, cy):   return (cx + 7.62, cy)          # MC78L05 VO(出力)
def ic1_gnd(cx, cy):  return (cx, cy + 7.62)          # MC78L05 GND
def oa_plus(cx, cy):  return (cx - 7.62, cy - 2.54)   # LM2904 +(非反転)
def oa_minus(cx, cy): return (cx - 7.62, cy + 2.54)   # LM2904 -(反転)
def oa_out(cx, cy):   return (cx + 7.62, cy)          # LM2904 Out

# ============================================================
# 追加要素リスト
# ============================================================
adds = []

# ──────────────────────────────────────────────
# 1. バイパスコン・デカップ全下端 → GND
# ──────────────────────────────────────────────
BYPASS_CAPS = [
    # ref,     cx,     cy
    ("C100", 132.08, 132.08),
    ("C101", 154.94, 132.08),
    ("C102", 172.72, 175.26),
    ("C103", 182.88, 132.08),
    ("C104", 236.22, 132.08),
    ("C105", 299.72, 147.32),
    ("C106", 162.56, 444.50),
    ("C107",  88.90, 419.10),
    ("C108", 175.26, 279.40),
    ("C109", 210.82, 279.40),
    ("C110", 284.48, 294.64),
    ("C111", 355.60, 304.80),
    ("C112", 381.00, 330.20),
    ("C113", 373.38, 414.02),
    ("C114", 614.68, 330.20),
    ("C115", 678.18, 317.50),
    ("C116", 749.30, 330.20),
    ("C117", 478.54, 492.76),
    ("C118", 513.08, 492.76),
    ("C119", 328.42, 507.00),
    ("C120", 429.26, 543.56),
    ("C150", 289.56, 154.94),
    ("C151", 431.80, 152.40),
    ("C152", 490.22, 147.32),
    ("C153", 520.70, 147.32),
    ("C154", 548.64, 127.00),
    ("C155", 323.34, 543.56),
    ("C156", 510.54, 513.08),
    ("C157", 599.44, 487.68),
    ("C158", 622.30, 487.68),
    ("C159", 733.44, 472.44),
    ("C160", 787.40, 490.22),
    ("C5",   457.20, 152.40),
    ("C25",  795.02, 284.48),
    ("C8",   800.10,  55.88),
    ("C8b",  762.00,  83.82),
]
for ref, cx, cy in BYPASS_CAPS:
    bx, by = r_bot(cx, cy)
    adds.append(gnd(bx, by))

# ──────────────────────────────────────────────
# 2. IC1 (LP2950L-5.0V) 電源ピン接続
#    IC1 at (762.00, 55.88)
# ──────────────────────────────────────────────
IC1_X, IC1_Y = 762.00, 55.88
adds.append(pwr9v(*ic1_vi(IC1_X, IC1_Y)))   # VI → +9V
adds.append(pwr5v(*ic1_vo(IC1_X, IC1_Y)))   # VO → +5V
adds.append(gnd(*ic1_gnd(IC1_X, IC1_Y)))    # GND

# C8 上端 → +9V, C8b 上端 → +5V
adds.append(pwr9v(*r_top(800.10, 55.88)))
adds.append(pwr5v(*r_top(762.00, 83.82)))

# ──────────────────────────────────────────────
# 3. RF_AMP 電源・バイアス接続
# ──────────────────────────────────────────────
# R1 (120kΩ, Q1 G2バイアス上): 上端 → +9V
adds.append(pwr9v(*r_top(193.04, 116.84)))
# R14 (20kΩ, Q1 G2バイアス下): 下端 → GND
adds.append(gnd(*r_bot(193.04, 137.16)))

# R1 下端 - R14 上端の接続ワイヤ (同じX=193.04)
adds.append(wire(193.04, 120.65, 193.04, 133.35))

# Q1 G2 ← R1/R14 ジャンクション接続ワイヤ
# R1-R14 中点 y = 127.0, Q1 G2 = (172.72, 96.52)
# 中点から G2 へ: 水平→垂直
adds.append(wire(193.04, 127.00, 172.72, 127.00))   # 水平
adds.append(wire(172.72, 127.00, 172.72, 96.52))    # 垂直

# Q1 S (ソース) → C103 上端
# Q1 at (177.80, 93.98): S = (180.34, 99.06)
# C103 at (182.88, 132.08): top = (182.88, 128.27)
# ワイヤ: Q1 S→右→下→C103 top
adds.append(wire(180.34, 99.06, 182.88, 99.06))
adds.append(wire(182.88, 99.06, 182.88, 128.27))

# Q1 D (ドレイン) → C2 上端 (15p 結合コンデンサ)
# Q1 D = (180.34, 88.90), C2 at (215.90, 106.68): top = (215.90, 102.87)
adds.append(wire(180.34, 88.90, 180.34, 71.12))   # Q1 D から上へ
adds.append(wire(180.34, 71.12, 215.90, 71.12))   # 水平
adds.append(wire(215.90, 71.12, 215.90, 102.87))  # C2 top まで下へ

# L1 二次上端 (SB) → C1 上端
# L1 at (132.08, 76.20): SB = (143.24, 71.12)
# C1 at (154.94, 106.68): top = (154.94, 102.87)
adds.append(wire(143.24, 71.12, 154.94, 71.12))
adds.append(wire(154.94, 71.12, 154.94, 102.87))

# C1 下端 → Q1 G1
# C1 bottom = (154.94, 110.49), Q1 G1 = (172.72, 91.44)
adds.append(wire(154.94, 110.49, 154.94, 91.44))
adds.append(wire(154.94, 91.44, 172.72, 91.44))

# L1 一次中点 / L2 一次 → +9V
# L1 AA (一次上) = (121.92, 71.12) → ネットラベル "ANT"
adds.append(netlabel("ANT", *tr_AA(132.08, 76.20)))
# L2 SB (二次上) = (246.38, 71.12) → ネットラベル "RF_DET"
adds.append(netlabel("RF_DET", *tr_SB(236.22, 76.20)))

# L1/L2 一次中点 → +9V (センタータップ)
# L1 SA (二次下) at (143.24, 81.28) → 通常 AC Ground 用
# L2 AA (一次上) at (226.06, 71.12) → +9V 供給
adds.append(pwr9v(*tr_AA(236.22, 76.20)))  # L2 一次上端 → +9V

# ──────────────────────────────────────────────
# 4. DETECTOR 接続
# ──────────────────────────────────────────────
# Q2 at (299.72, 83.82)
# R2 (1MΩ, ベースバイアス): 上端 → +9V, 下端 → Q2 B
adds.append(pwr9v(*r_top(289.56, 116.84)))

# R2 下端 → Q2 B ワイヤ
# R2 bottom = (289.56, 120.65), Q2 B = (294.64, 83.82)
adds.append(wire(289.56, 120.65, 289.56, 83.82))
adds.append(wire(289.56, 83.82, 294.64, 83.82))

# R21 (4.7kΩ, エミッタ抵抗): 下端 → GND
adds.append(gnd(*r_bot(322.58, 116.84)))

# Q2 E → R21 上端
# Q2 E = (302.26, 88.90), R21 top = (322.58, 113.03)
adds.append(wire(302.26, 88.90, 322.58, 88.90))
adds.append(wire(322.58, 88.90, 322.58, 113.03))

# Q2 C → ネットラベル "AF_IN" (AF段入力)
adds.append(netlabel("AF_IN", *npn_c(299.72, 83.82)))

# Q2 ベース入力 ← C3 (検波コンデンサ)
# C3 at (299.72, 99.06): top = (299.72, 95.25)
# Q2 B = (294.64, 83.82), C3 top = (299.72, 95.25)
adds.append(wire(294.64, 83.82, 294.64, 95.25))
adds.append(wire(294.64, 95.25, 299.72, 95.25))

# R5 (1kΩ) 下端 → GND (検波出力抵抗下端)
adds.append(gnd(*r_bot(309.88, 132.08)))

# ──────────────────────────────────────────────
# 5. AF_AMP 電源・バイアス
# ──────────────────────────────────────────────
# Q3 at (431.80, 76.20), Q4 at (490.22, 76.20)
# Q5 at (548.64, 55.88), Q6 at (548.64, 99.06)

# R6 (100kΩ, Q3ベースバイアス上): 上端 → +9V
adds.append(pwr9v(*r_top(436.88, 116.84)))

# R8 (100kΩ, Q4バイアス): 上端 → +9V
adds.append(pwr9v(*r_top(500.38, 99.06)))

# R11 (10kΩ, Q5コレクタ): 上端 → +9V
adds.append(pwr9v(*r_top(558.80, 55.88)))

# R12 (10kΩ, Q6エミッタ側): GND 接続
adds.append(gnd(*r_bot(558.80, 76.20)))

# R7 下端 → GND (Q3 エミッタ抵抗)
adds.append(gnd(*r_bot(449.58, 142.24)))
# R9 下端 → GND (Q4 エミッタ抵抗)
adds.append(gnd(*r_bot(518.16, 142.24)))
# R15 下端 → GND (SP抵抗)
adds.append(gnd(*r_bot(553.72, 137.16)))
# R43 下端 → GND
adds.append(gnd(*r_bot(503.94, 142.24)))

# VR2 (10kΩ 音量): 下端 → GND
adds.append(gnd(*vr_bot(495.30, 157.48)))

# Q5 C (上) → ネットラベル "+9V" 系 (R11 経由)
adds.append(netlabel("AF_OUT", *npn_c(548.64, 55.88)))

# C28 (100μF, PHONE出力): 上端 → ネットラベル "PHONE"
adds.append(netlabel("PHONE", *r_top(558.80, 25.40)))
# C28 下端 → GND
adds.append(gnd(*r_bot(558.80, 25.40)))

# ──────────────────────────────────────────────
# 6. POWER ブロック追加接続
# ──────────────────────────────────────────────
# SW1 (電源SW) at (695.96, 88.90): SW_SPST ピン確認後に対応
# R13 (1kΩ, LED電流制限): 上端 → +9V 系
adds.append(pwr9v(*r_top(695.96, 127.00)))
# LED1 下端 (カソード, 左) → GND
# LED1 at (695.96, 152.40), K = (695.96 - 3.81, 152.40) = (692.15, 152.40)
adds.append(gnd(692.15, 152.40))
# R13 下端 → LED1 アノード (右)
# R13 bottom = (695.96, 130.81), LED1 A = (699.77, 152.40)
adds.append(wire(695.96, 130.81, 695.96, 152.40))
adds.append(wire(695.96, 152.40, 699.77, 152.40))

# ──────────────────────────────────────────────
# 7. VXO ブロック電源
# ──────────────────────────────────────────────
# Q8 at (614.68, 309.88), Q7 at (678.18, 289.56)
# C25 (10μF, VXO電源デカップ): 上端 → +9V
adds.append(pwr9v(*r_top(795.02, 284.48)))

# R17 (100kΩ): 上端 → +9V (Q7/Q8 コレクタ供給)
adds.append(pwr9v(*r_top(759.46, 289.56)))
# R16 (10kΩ): 下端 → GND
adds.append(gnd(*r_bot(764.54, 327.66)))
# R19 (220kΩ): 上端 → +9V (Q8バイアス)
adds.append(pwr9v(*r_top(635.00, 337.82)))
# R18 (1kΩ): 下端 → GND (Q7 エミッタ)
adds.append(gnd(*r_bot(678.18, 332.74)))

# Q7/Q8 出力 → ネットラベル "VXO_OUT"
# Q7 C = (680.72, 284.48) ... L3 経由
adds.append(netlabel("VXO_OUT", *tr_SA(782.32, 284.48)))

# ──────────────────────────────────────────────
# 8. RF_PSN ブロック
# ──────────────────────────────────────────────
# Q9 at (381.00, 289.56), Q10 at (449.58, 335.28)
# R42 (100kΩ, Q9ゲートバイアス → GND): 下端 → GND
adds.append(gnd(*r_bot(381.00, 304.80)))
# R42 上端 → Q9 G へのネットラベル
adds.append(netlabel("RF_PSN_BIAS_A", *r_top(381.00, 304.80)))
adds.append(netlabel("RF_PSN_BIAS_A", *jfet_g(381.00, 289.56)))
# R20 (100kΩ, Q10ゲートバイアス → GND): 下端 → GND
adds.append(gnd(*r_bot(449.58, 350.52)))
# R20 上端 → Q10 G へのネットラベル
adds.append(netlabel("RF_PSN_BIAS_B", *r_top(449.58, 350.52)))
adds.append(netlabel("RF_PSN_BIAS_B", *jfet_g(449.58, 335.28)))

# ──────────────────────────────────────────────
# 9. DRIVER ブロック (Q14 2SK439)
# ──────────────────────────────────────────────
# Q14 at (497.84, 477.52)
# R36 (51Ω "ソース") at (503.18, 459.74): Q14 D 上のシリーズ抵抗 → 上端 +9V
adds.append(pwr9v(*r_top(503.18, 459.74)))
# R36 下端 → Q14 D ネットラベル
adds.append(netlabel("Q14_DRAIN", *r_bot(503.18, 459.74)))
adds.append(netlabel("Q14_DRAIN", *jfet_d(497.84, 477.52)))
# R46 (51Ω "ドレイン") at (492.76, 492.76): Q14 S 下のソース抵抗 → 下端 GND
adds.append(gnd(*r_bot(492.76, 492.76)))
# R46 上端 → Q14 S ネットラベル
adds.append(netlabel("Q14_SRC", *r_top(492.76, 492.76)))
adds.append(netlabel("Q14_SRC", *jfet_s(497.84, 477.52)))
# 入出力ネットラベル
adds.append(netlabel("DRIVER_IN",  *jfet_g(497.84, 477.52)))
adds.append(netlabel("DRIVER_OUT", *jfet_d(497.84, 477.52)))

# ──────────────────────────────────────────────
# 10. BAL_MOD ブロック
# ──────────────────────────────────────────────
# Q13 at (429.26, 558.80): NPN トランジスタ
# R29 (4.7kΩ) 上端 → +9V
adds.append(pwr9v(*r_top(393.70, 538.48)))
# R29 下端 → GND
adds.append(gnd(*r_bot(393.70, 538.48)))
# R32 下端 → GND
adds.append(gnd(*r_bot(383.54, 543.56)))
# R33 下端 → GND (エミッタ抵抗)
adds.append(gnd(*r_bot(398.78, 563.88)))
# Q13 E → R33 上端 (ネットラベルで接続)
adds.append(netlabel("Q13_E", *npn_e(429.26, 558.80)))
adds.append(netlabel("Q13_E", *r_top(398.78, 563.88)))

# ──────────────────────────────────────────────
# 11. AF_PSN ブロック
# ──────────────────────────────────────────────
# IC2 (NJM2904) at (553.72, 487.68): LM2904 OPアンプ
# R27 (10kΩ) 上端 → +9V (IC2電源供給 or バイアス)
adds.append(pwr9v(*r_top(553.72, 449.58)))
# R26 (10kΩ) 上端 → 接続
# R30 (22Ω) 下端 → GND (出力抵抗)
adds.append(gnd(*r_bot(515.62, 508.00)))

# IC2 出力 → ネットラベル
adds.append(netlabel("AF_PSN_OUT", *oa_out(553.72, 487.68)))

# Q12 at (510.54, 490.22): 信号分割 NPN
adds.append(netlabel("MIC_SIG", *npn_b(510.54, 490.22)))

# ──────────────────────────────────────────────
# 12. MIC_AMP ブロック
# ──────────────────────────────────────────────
# Q11 at (754.38, 472.44): マイクアンプ NPN
# R24 (1kΩ) 上端 → +9V
adds.append(pwr9v(*r_top(759.46, 439.42)))
# R23 (100kΩ) 上端 → +9V
adds.append(pwr9v(*r_top(749.30, 454.66)))
# R25b (330Ω, エミッタ) 下端 → GND
adds.append(gnd(*r_bot(754.38, 508.00)))
# R22 (1kΩ, MICバイアス) 上端 → +9V (マイクバイアス供給)
adds.append(pwr9v(*r_top(787.40, 462.28)))

# Q11 E → R25b 上端
# Q11 E = (756.92, 477.52), R25b top = (754.38, 504.19)
adds.append(wire(756.92, 477.52, 756.92, 504.19))
adds.append(wire(756.92, 504.19, 754.38, 504.19))

# ──────────────────────────────────────────────
# 13. FINAL ブロック
# ──────────────────────────────────────────────
# Q15 at (162.56, 429.26), Q16 at (88.90, 449.58)
# R40 (1kΩ) 上端 → +9V
adds.append(pwr9v(*r_top(96.52, 462.28)))
# R41 (100Ω, Q16エミッタ) 下端 → GND
adds.append(gnd(*r_bot(104.14, 497.84)))
# R38 (4.7kΩ) 上端 → +9V (Q15バイアス)
adds.append(pwr9v(*r_top(180.34, 432.80)))
# R39 (51Ω) 下端 → GND
adds.append(gnd(*r_bot(170.18, 444.50)))

# LED2 カソード (左) → GND
# LED2 at (96.52, 449.58): K = (92.71, 449.58)
adds.append(gnd(92.71, 449.58))

# 出力ネットラベル
# L15 SA (二次下) → アンテナ出力
adds.append(netlabel("TX_OUT", *tr_SA(27.94, 370.84)))

# ──────────────────────────────────────────────
# 14. 主要ブロック間ネットラベル (信号経路)
# ──────────────────────────────────────────────
# L2 二次上端 → 検波入力
adds.append(netlabel("RF_DET", *tr_AB(236.22, 76.20)))

# Q2 コレクタ (検波出力 → AF入力)
# Q2 C = (302.26, 78.74)
adds.append(netlabel("AF_IN", 302.26, 78.74))

# Q3 ベース (AF段入力)
# Q3 at (431.80, 76.20): B = (426.72, 76.20)
adds.append(netlabel("AF_IN", *npn_b(431.80, 76.20)))

# VXO出力 → RF_PSN入力
# L3 二次下端 → RF_PSN L6 一次
adds.append(netlabel("VXO_OUT", *tr_AB(782.32, 284.48)))
# L6 一次上端 ← VXO_OUT
adds.append(netlabel("VXO_OUT", *tr_AA(284.48, 264.16)))

# RF_PSN 出力 → BAL_MOD
adds.append(netlabel("RF_PSN_OUT", *jfet_d(449.58, 335.28)))

# MIC_AMP 出力 → AF_PSN 入力
# Q11 C = (756.92, 467.36)
adds.append(netlabel("MIC_SIG", *npn_c(754.38, 472.44)))

print(f"追加要素数: {len(adds)}")

# ============================================================
# ファイル更新
# ============================================================
def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 末尾の ")" の直前に挿入
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

if __name__ == "__main__":
    main()
