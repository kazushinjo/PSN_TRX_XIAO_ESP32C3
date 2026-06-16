#!/usr/bin/env python3
"""
PSN_TRX KiCad 10.0 Schematic Generator V2
JPG忠実配置版 - 全部品に絶対座標を個別指定

元回路図: C:\\Users\\kazus\\Downloads\\PSN.jpg (4207x2982px @600dpi)
スケール: 1mm ≈ 5px → KiCad座標(mm) = px / 5、2.54mmグリッドスナップ

C98(1μF)/C99(0.01μF)系バイパスコンは個別番号に展開:
  C99系(0.01μF) → C100〜C149
  C98系(1μF)   → C150〜C199
"""

import uuid, re, os

KICAD_SYM_DIR = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"
OUTPUT_PATH   = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"

def gen_uuid():
    return str(uuid.uuid4())

# ============================================================
# 使用シンボル
# ============================================================
NEEDED_SYMBOLS = [
    ("Device",                "R"),
    ("Device",                "C"),
    ("Device",                "L"),
    ("Device",                "Transformer_1P_1S"),
    ("Device",                "Crystal"),
    ("Device",                "D"),
    ("Device",                "LED"),
    ("Device",                "R_Potentiometer"),
    ("Device",                "Q_NJFET_GDS"),
    ("Transistor_BJT",        "Q_NPN_BCE"),
    ("Transistor_BJT",        "Q_PNP_BCE"),
    ("Transistor_FET",        "3SK263"),
    ("Amplifier_Operational", "LM2904"),
    ("Regulator_Linear",      "MC78L05_TO92"),
    ("Switch",                "SW_SPDT"),
    ("Switch",                "SW_SPST"),
    ("Connector_Generic",     "Conn_01x02"),
    ("power",                 "GND"),
    ("power",                 "+9V"),
    ("power",                 "+5V"),
]

# ============================================================
# 部品定義: (ref, value, lib_sym, x_mm, y_mm, rot, desc)
# 座標はJPGピクセル/5 → 2.54mmグリッドスナップ
# ============================================================

# --- 高周波増幅 (RF AMP) JPG左上エリア ---
COMP_RF_AMP = [
    ("SW2",  "送受切替",  "Switch:SW_SPDT",              48.26, 119.38,  0, "送受切替"),
    ("L1",   "7T50",      "Device:Transformer_1P_1S",   132.08,  76.20,  0, "7mm角50MHz用トランス"),
    ("C1",   "15p",       "Device:C",                   154.94, 106.68,  0, "G1結合"),
    ("C100", "0.01u",     "Device:C",                   132.08, 132.08,  0, "L1一次GND"),
    ("C101", "0.01u",     "Device:C",                   154.94, 132.08,  0, "L1二次GND"),
    ("Q1",   "3SK59",     "Transistor_FET:3SK263",      177.80,  93.98,  0, "高周波増幅"),
    ("R1",   "120k",      "Device:R",                   193.04, 116.84,  0, "G2バイアス上"),
    ("R14",  "20k",       "Device:R",                   193.04, 137.16,  0, "G2バイアス下"),
    ("VR1",  "5k",        "Device:R_Potentiometer",     172.72, 160.02,  0, "AGC調整"),
    ("C102", "0.01u",     "Device:C",                   172.72, 175.26,  0, "VR1バイパス"),
    ("C103", "0.01u",     "Device:C",                   182.88, 132.08,  0, "Q1ソースGND"),
    ("C2",   "15p",       "Device:C",                   215.90, 106.68,  0, "ドレイン結合"),
    ("C104", "0.01u",     "Device:C",                   236.22, 132.08,  0, "L2一次GND"),
    ("L2",   "7T50",      "Device:Transformer_1P_1S",   236.22,  76.20,  0, "7mm角50MHz用トランス"),
]

# --- 検波 (DETECTOR) JPG上中エリア ---
COMP_DETECTOR = [
    ("Q2",   "2SC1923",   "Transistor_BJT:Q_NPN_BCE",   299.72,  83.82,  0, "検波"),
    ("R2",   "1M",        "Device:R",                   289.56, 116.84, 0, "バイアス"),
    ("R21",  "4.7k",      "Device:R",                   322.58, 116.84, 0, "エミッタ抵抗"),
    ("R5",   "1k",        "Device:R",                   309.88, 132.08, 0, ""),
    ("C3",   "0.001u",    "Device:C",                   299.72,  99.06, 0, "検波コンデンサ"),
    ("C105", "0.01u",     "Device:C",                   299.72, 147.32, 0, "Q2バイパス"),
    ("C150", "1u",        "Device:C",                   289.56, 154.94, 0, "C98系バイパス"),
]

# --- 低周波増幅 (AF AMP) JPG上中右エリア ---
COMP_AF_AMP = [
    ("Q3",   "2SC1815",   "Transistor_BJT:Q_NPN_BCE",   431.80,  76.20,  0, "AF初段"),
    ("Q4",   "2SC1815",   "Transistor_BJT:Q_NPN_BCE",   490.22,  76.20,  0, "AF2段"),
    ("Q5",   "2SC2120",   "Transistor_BJT:Q_NPN_BCE",   548.64,  55.88,  0, "出力NPN"),
    ("Q6",   "2SA950",    "Transistor_BJT:Q_PNP_BCE",   548.64,  99.06,  0, "出力PNP"),
    ("R6",   "100k",      "Device:R",                   436.88, 116.84, 0, ""),
    ("R4",   "1.5k",      "Device:R",                   495.30, 116.84, 0, ""),
    ("R7",   "1k",        "Device:R",                   449.58, 142.24, 0, ""),
    ("R8",   "100k",      "Device:R",                   500.38,  99.06, 0, ""),
    ("R9",   "1k",        "Device:R",                   518.16, 142.24, 0, ""),
    ("R10",  "1k",        "Device:R",                   535.94,  99.06, 0, ""),
    ("R11",  "10k",       "Device:R",                   558.80,  55.88, 0, ""),
    ("R12",  "10k",       "Device:R",                   558.80,  76.20, 0, ""),
    ("R15",  "100",       "Device:R",                   553.72, 137.16, 0, "SP抵抗"),
    ("R43",  "330",       "Device:R",                   503.94, 142.24, 0, ""),
    ("VR2",  "10k",       "Device:R_Potentiometer",     495.30, 157.48, 0, "音量調整"),
    ("C4",   "0.1u",      "Device:C",                   462.28,  99.06, 0, ""),
    ("C5",   "10u",       "Device:C",                   457.20, 152.40, 0, ""),
    ("C6",   "0.1u",      "Device:C",                   505.46,  88.90, 0, ""),
    ("C7",   "0.1u",      "Device:C",                   436.88,  88.90, 0, ""),
    ("C28",  "100u",      "Device:C",                   558.80,  25.40, 0, "PHONE出力"),
    ("C29",  "1u",        "Device:C",                   548.64, 157.48, 0, ""),
    ("C151", "1u",        "Device:C",                   431.80, 152.40, 0, "C98系バイパス"),
    ("C152", "1u",        "Device:C",                   490.22, 147.32, 0, "C98系バイパス"),
    ("C153", "1u",        "Device:C",                   520.70, 147.32, 0, "C98系バイパス"),
    ("C154", "1u",        "Device:C",                   548.64, 127.00, 0, "C98系バイパス"),
]

# --- 電源 (POWER) JPG右上エリア ---
COMP_POWER = [
    ("IC1",  "LP2950L-5.0V", "Regulator_Linear:MC78L05_TO92", 762.00, 55.88, 0, "5V安定化"),
    ("C8",   "10u",          "Device:C",                      800.10, 55.88, 0, "入力デカップ"),
    ("C8b",  "10u",          "Device:C",                      762.00, 83.82, 0, "出力デカップ"),
    ("R13",  "1k",           "Device:R",                      695.96, 127.00, 0, "LED電流制限"),
    ("LED1", "LED",          "Device:LED",                    695.96, 152.40, 0, "電源表示"),
    ("SW1",  "SW",           "Switch:SW_SPST",                695.96, 88.90,  0, "電源SW"),
]

# --- 終段増幅 (FINAL AMP) JPG左中エリア ---
COMP_FINAL = [
    ("L15",  "T-50-10",   "Device:Transformer_1P_1S",    27.94, 370.84,  0, "T-50-10 18回"),
    ("L14",  "T-50-10",   "Device:Transformer_1P_1S",    55.88, 370.84,  0, "T-50-10 18回"),
    ("TC3",  "30p",       "Device:C",                    58.42, 452.12, 0, "トリマ"),
    ("D5",   "1N60",      "Device:D",                    88.90, 378.46,  0, ""),
    ("D6",   "1N60",      "Device:D",                    88.90, 393.70,  0, ""),
    ("LED2", "LED黄",      "Device:LED",                  96.52, 449.58,  0, "送信表示"),
    ("R40",  "1k",        "Device:R",                    96.52, 462.28, 0, ""),
    ("R41",  "100",       "Device:R",                   104.14, 497.84, 0, ""),
    ("Q16",  "2SC1815",   "Transistor_BJT:Q_NPN_BCE",    88.90, 449.58,  0, "終段"),
    ("R38",  "4.7k",      "Device:R",                   180.34, 432.80, 0, ""),
    ("R39",  "51",        "Device:R",                   170.18, 444.50, 0, ""),
    ("Q15",  "2SC1815",   "Transistor_BJT:Q_NPN_BCE",   162.56, 429.26,  0, "終段"),
    ("R37",  "20k",       "Device:R",                    35.56, 279.40, 0, ""),
    ("L13b", "7T50",      "Device:Transformer_1P_1S",   198.12, 264.16,  0, "合成コイル"),
    ("L12",  "7T50",      "Device:Transformer_1P_1S",   160.02, 264.16,  0, ""),
    ("C26",  "15p",       "Device:C",                   162.56, 279.40, 0, ""),
    ("C27",  "5p",        "Device:C",                   198.12, 279.40, 0, ""),
    ("C106", "0.01u",     "Device:C",                   162.56, 444.50, 0, "Q15バイパス"),
    ("C107", "0.01u",     "Device:C",                    88.90, 419.10, 0, "Q16バイパス"),
    ("C108", "0.01u",     "Device:C",                   175.26, 279.40, 0, "L12バイパス"),
    ("C109", "0.01u",     "Device:C",                   210.82, 279.40, 0, "L13バイパス"),
]

# --- RF PSN JPG中央エリア ---
COMP_RF_PSN = [
    ("L6",   "7T50",      "Device:Transformer_1P_1S",   284.48, 264.16,  0, "7mm角50MHz"),
    ("C17",  "15p",       "Device:C",                   284.48, 279.40, 0, ""),
    ("C110", "0.01u",     "Device:C",                   284.48, 294.64, 0, "L6バイパス"),
    ("Q9",   "2SK439",    "Device:Q_NJFET_GDS",         381.00, 289.56,  0, "RF移相器"),
    ("R42",  "100k",      "Device:R",                   381.00, 304.80, 0, ""),
    ("R51",  "51",        "Device:R",                   342.90, 289.56, 0, ""),
    ("C111", "0.01u",     "Device:C",                   355.60, 304.80, 0, "Q9バイパス"),
    ("C112", "0.01u",     "Device:C",                   381.00, 330.20, 0, "Q9バイパス"),
    ("L7",   "7T50",      "Device:Transformer_1P_1S",   373.38, 383.54,  0, "7mm角50MHz"),
    ("C18",  "15p",       "Device:C",                   373.38, 398.78, 0, ""),
    ("C113", "0.01u",     "Device:C",                   373.38, 414.02, 0, "L7バイパス"),
    ("Q10",  "2SK439",    "Device:Q_NJFET_GDS",         449.58, 335.28,  0, "RF移相器"),
    ("R20",  "100k",      "Device:R",                   449.58, 350.52, 0, ""),
    ("R52",  "51",        "Device:R",                   416.56, 335.28, 0, ""),
]

# --- VXO JPG右中エリア ---
COMP_VXO = [
    ("Q8",   "2SC1923",   "Transistor_BJT:Q_NPN_BCE",   614.68, 309.88,  0, "VXO発振"),
    ("TC2",  "5p",        "Device:C",                   614.68, 248.92, 0, "トリマ"),
    ("TC1",  "40p",       "Device:C",                   629.92, 248.92, 0, "トリマ"),
    ("C11",  "47p",       "Device:C",                   649.86, 358.14, 0, ""),
    ("C13",  "5p",        "Device:C",                   635.00, 269.24, 0, ""),
    ("C14",  "4p",        "Device:C",                   640.08, 368.30, 0, ""),
    ("R19",  "220k",      "Device:R",                   635.00, 337.82, 0, ""),
    ("R18",  "1k",        "Device:R",                   678.18, 332.74, 0, ""),
    ("Q7",   "2SC1923",   "Transistor_BJT:Q_NPN_BCE",   678.18, 289.56,  0, "VXO増幅"),
    ("C10",  "47p",       "Device:C",                   723.90, 259.08, 0, ""),
    ("C12",  "47p",       "Device:C",                   710.82, 355.60, 0, ""),
    ("X1",   "50.5MHz/3", "Device:Crystal",             744.22, 289.56,  0, "水晶振動子"),
    ("C9",   "100p",      "Device:C",                   749.30, 317.50, 0, ""),
    ("L3",   "7T5",       "Device:Transformer_1P_1S",   782.32, 284.48,  0, "VXOコイル"),
    ("R17",  "100k",      "Device:R",                   759.46, 289.56, 0, ""),
    ("R16",  "10k",       "Device:R",                   764.54, 327.66, 0, ""),
    ("C25",  "10u",       "Device:C",                   795.02, 284.48, 0, "VXO電源デカップ"),
    ("C114", "0.01u",     "Device:C",                   614.68, 330.20, 0, "Q8バイパス"),
    ("C115", "0.01u",     "Device:C",                   678.18, 317.50, 0, "Q7バイパス"),
    ("C116", "0.01u",     "Device:C",                   749.30, 330.20, 0, "X1バイパス"),
]

# --- 励振増幅 (DRIVER) JPG下中エリア ---
COMP_DRIVER = [
    ("Q14",  "2SK439",    "Device:Q_NJFET_GDS",         497.84, 477.52,  0, "励振増幅"),
    ("R36",  "51",        "Device:R",                   503.18, 459.74, 0, "ソース"),
    ("R46",  "51",        "Device:R",                   492.76, 492.76, 0, "ドレイン"),
    ("C23",  "15p",       "Device:C",                   478.54, 462.28, 0, ""),
    ("C24",  "15p",       "Device:C",                   513.08, 462.28, 0, ""),
    ("C117", "0.01u",     "Device:C",                   478.54, 492.76, 0, "Q14バイパス"),
    ("C118", "0.01u",     "Device:C",                   513.08, 492.76, 0, "Q14バイパス"),
]

# --- 平衡変調・合成 (BAL MOD) JPG下中エリア ---
COMP_BAL_MOD = [
    ("L11",  "7T50",      "Device:Transformer_1P_1S",   264.16, 459.74,  0, "合成コイル"),
    ("C22",  "15p",       "Device:C",                   264.16, 477.52, 0, ""),
    ("L13",  "7T50",      "Device:Transformer_1P_1S",   231.14, 459.74,  0, ""),
    ("R35",  "100k",      "Device:R",                   391.16, 459.74, 0, ""),
    ("R34",  "100",       "Device:R",                   383.54, 477.52, 0, ""),
    ("C19",  "33p",       "Device:C",                   388.62, 459.74, 0, ""),
    ("C20",  "0.001u",    "Device:C",                   391.16, 492.76, 0, ""),
    ("C21",  "0.001u",    "Device:C",                   338.58, 492.76, 0, ""),
    ("VR4",  "1k",        "Device:R_Potentiometer",     419.10, 477.52, 0, "キャリア調整"),
    ("VR5",  "1k",        "Device:R_Potentiometer",     411.48, 490.22, 0, ""),
    ("L10",  "1mH",       "Device:L",                   323.34, 487.68,  0, ""),
    ("L9",   "1mH",       "Device:L",                   328.42, 536.58,  0, ""),
    ("D1",   "1N60",      "Device:D",                   348.74, 502.92,  0, "平衡変調"),
    ("D2",   "1N60",      "Device:D",                   356.36, 502.92,  0, ""),
    ("D3",   "1N60",      "Device:D",                   363.98, 502.92,  0, ""),
    ("D4",   "1N60",      "Device:D",                   371.60, 502.92,  0, ""),
    ("R29",  "4.7k",      "Device:R",                   393.70, 538.48, 0, ""),
    ("R31",  "1M",        "Device:R",                   408.94, 530.86, 0, ""),
    ("R32",  "4.7k",      "Device:R",                   383.54, 543.56, 0, ""),
    ("R33",  "22",        "Device:R",                   398.78, 563.88, 0, ""),
    ("Q13",  "2SC1815",   "Transistor_BJT:Q_NPN_BCE",   429.26, 558.80,  0, ""),
    ("C119", "0.01u",     "Device:C",                   328.42, 507.00, 0, "D1-D4バイパス"),
    ("C120", "0.01u",     "Device:C",                   429.26, 543.56, 0, "Q13バイパス"),
    ("C155", "1u",        "Device:C",                   323.34, 543.56, 0, "C98系バイパス"),
]

# --- AF PSN・信号分割 JPG下中右エリア ---
COMP_AF_PSN = [
    ("Q12",  "2SC1815",   "Transistor_BJT:Q_NPN_BCE",   510.54, 490.22,  0, ""),
    ("IC2",  "NJM2904",   "Amplifier_Operational:LM2904", 553.72, 487.68, 0, "AF PSN 1/2"),
    ("R27",  "10k",       "Device:R",                   553.72, 449.58, 0, ""),
    ("R26",  "10k",       "Device:R",                   563.88, 472.44, 0, ""),
    ("R25",  "10k",       "Device:R",                   528.32, 472.44, 0, ""),
    ("R28",  "1M",        "Device:R",                   523.24, 480.06, 0, ""),
    ("VR3",  "10k",       "Device:R_Potentiometer",     568.96, 495.30, 0, "位相調整"),
    ("C15",  "10u",       "Device:C",                   599.44, 462.28, 0, ""),
    ("C16",  "0.1u",      "Device:C",                   553.72, 508.00, 0, ""),
    ("R30",  "22",        "Device:R",                   515.62, 508.00, 0, ""),
    ("L8",   "15mH",      "Device:Transformer_1P_1S",   617.22, 462.28,  0, "ST-71音声トランス"),
    ("C156", "1u",        "Device:C",                   510.54, 513.08, 0, "C98系バイパス"),
    ("C157", "1u",        "Device:C",                   599.44, 487.68, 0, "C98系バイパス"),
    ("C158", "1u",        "Device:C",                   622.30, 487.68, 0, "L8バイパス"),
]

# --- マイクアンプ (MIC AMP) JPG右下エリア ---
COMP_MIC_AMP = [
    ("Q11",  "2SC1815",   "Transistor_BJT:Q_NPN_BCE",   754.38, 472.44,  0, "マイクアンプ"),
    ("R24",  "1k",        "Device:R",                   759.46, 439.42, 0, ""),
    ("R23",  "100k",      "Device:R",                   749.30, 454.66, 0, ""),
    ("R22",  "1k",        "Device:R",                   787.40, 462.28, 0, "MICバイアス"),
    ("R25b", "330",       "Device:R",                   754.38, 508.00, 0, "エミッタ"),
    ("MIC1", "MIC",       "Connector_Generic:Conn_01x02", 819.15, 469.90, 0, "マイク"),
    ("C159", "1u",        "Device:C",                   733.44, 472.44, 0, "C98系入力"),
    ("C160", "1u",        "Device:C",                   787.40, 490.22, 0, "C98系バイパス"),
]

# 全部品リスト
ALL_COMPONENTS = (
    COMP_RF_AMP + COMP_DETECTOR + COMP_AF_AMP + COMP_POWER +
    COMP_FINAL + COMP_RF_PSN + COMP_VXO + COMP_DRIVER +
    COMP_BAL_MOD + COMP_AF_PSN + COMP_MIC_AMP
)

# ============================================================
# ブロック枠
# ============================================================
BLOCK_FRAMES = [
    {"label": "高周波増幅",         "x1":  22.86, "y1":  43.18, "x2": 259.08, "y2": 200.66},
    {"label": "検波",               "x1": 271.78, "y1":  43.18, "x2": 340.36, "y2": 200.66},
    {"label": "低周波増幅",         "x1": 416.56, "y1":  15.24, "x2": 584.20, "y2": 200.66},
    {"label": "電源",               "x1": 680.72, "y1":  43.18, "x2": 819.15, "y2": 175.26},
    {"label": "終段増幅",           "x1":  15.24, "y1": 248.92, "x2": 231.14, "y2": 521.08},
    {"label": "RF PSN",             "x1": 271.78, "y1": 248.92, "x2": 475.74, "y2": 431.80},
    {"label": "VXO",                "x1": 599.44, "y1": 230.12, "x2": 819.15, "y2": 431.80},
    {"label": "励振増幅",           "x1": 462.28, "y1": 444.50, "x2": 535.94, "y2": 521.08},
    {"label": "合成・平衡変調",     "x1": 215.90, "y1": 444.50, "x2": 462.28, "y2": 584.20},
    {"label": "AF PSN・信号分割",   "x1": 496.57, "y1": 431.80, "x2": 645.16, "y2": 584.20},
    {"label": "マイクアンプ",       "x1": 714.12, "y1": 431.80, "x2": 838.20, "y2": 584.20},
]

# ============================================================
# シンボル抽出ユーティリティ
# ============================================================
def extract_symbol(lib_path, sym_name):
    try:
        with open(lib_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  [WARN] lib not found: {lib_path}")
        return None
    search = f'(symbol "{sym_name}"'
    pos = content.find(search)
    if pos == -1:
        print(f"  [WARN] symbol not found: {sym_name}")
        return None
    depth, i = 0, pos
    while i < len(content):
        if content[i] == '(':   depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0: return content[pos:i+1]
        i += 1
    return None

def sym_entry(sym_text, lib_name, sym_name, all_lib_map):
    new_name = f"{lib_name}:{sym_name}"
    result = re.sub(r'^\(symbol\s+"[^"]*"', f'(symbol "{new_name}"', sym_text, count=1)
    def fix_extends(m):
        pb = m.group(1)
        for (ln, sn) in all_lib_map:
            if sn == pb: return f'(extends "{ln}:{pb}")'
        return m.group(0)
    result = re.sub(r'\(extends\s+"([^"]+)"\)', fix_extends, result)
    return "\n".join("  " + l for l in result.splitlines())

def mm(v):
    return round(float(v), 4)

# ============================================================
# KiCad出力
# ============================================================
def write_component(ref, value, lib_sym, x, y, rot, desc):
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
        f'      (at {mm(x)} {mm(y-3.81)} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
        f'    (property "Value" "{value}"',
        f'      (at {mm(x)} {mm(y+3.81)} 0)',
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

def write_block_frame(f):
    cx = mm((f["x1"] + f["x2"]) / 2)
    return (
        f'  (rectangle (start {mm(f["x1"])} {mm(f["y1"])}) (end {mm(f["x2"])} {mm(f["y2"])})\n'
        f'    (stroke (width 0.2) (type default))\n'
        f'    (fill (type none))\n'
        f'    (uuid "{gen_uuid()}")\n'
        f'  )\n'
        f'  (text "{f["label"]}"\n'
        f'    (at {cx} {mm(f["y1"] - 3)} 0)\n'
        f'    (effects (font (size 2.54 2.54) bold))\n'
        f'    (uuid "{gen_uuid()}")\n'
        f'  )'
    )

# ============================================================
# メイン
# ============================================================
def main():
    print("=== KiCadシンボルライブラリ読み込み ===")
    collected = {}
    all_lib_map = set()
    for lib_name, sym_name in NEEDED_SYMBOLS:
        lib_path = os.path.join(KICAD_SYM_DIR, f"{lib_name}.kicad_sym")
        sym_text = extract_symbol(lib_path, sym_name)
        if sym_text:
            key = f"{lib_name}:{sym_name}"
            collected[key] = (sym_text, lib_name, sym_name)
            all_lib_map.add((lib_name, sym_name))
            print(f"  [OK] {key}")
        else:
            print(f"  [NG] {lib_name}:{sym_name}")

    print(f"\n=== 総部品数: {len(ALL_COMPONENTS)} ===")
    for block_name, comp_list in [
        ("RF_AMP", COMP_RF_AMP), ("DETECTOR", COMP_DETECTOR),
        ("AF_AMP", COMP_AF_AMP), ("POWER", COMP_POWER),
        ("FINAL", COMP_FINAL),   ("RF_PSN", COMP_RF_PSN),
        ("VXO", COMP_VXO),       ("DRIVER", COMP_DRIVER),
        ("BAL_MOD", COMP_BAL_MOD), ("AF_PSN", COMP_AF_PSN),
        ("MIC_AMP", COMP_MIC_AMP),
    ]:
        print(f"  {block_name}: {len(comp_list)}部品")

    lines = []
    lines.append("(kicad_sch")
    lines.append("  (version 20241209)")
    lines.append('  (generator "PSN_TRX_v2")')
    lines.append('  (generator_version "9.0")')
    lines.append('  (paper "A1")')
    lines.append("")

    # lib_symbols
    lines.append("  (lib_symbols")
    for key, (sym_text, lib_name, sym_name) in collected.items():
        lines.append(sym_entry(sym_text, lib_name, sym_name, all_lib_map))
    lines.append("  )")
    lines.append("")

    # ブロック枠
    for f in BLOCK_FRAMES:
        lines.append(write_block_frame(f))
    lines.append("")

    # 部品
    for comp in ALL_COMPONENTS:
        ref, value, lib_sym, x, y, rot, desc = comp
        lines.append(write_component(ref, value, lib_sym, x, y, rot, desc))
        lines.append("")

    lines.append(")")

    content = "\n".join(lines)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n生成完了: {OUTPUT_PATH}")
    print(f"ファイルサイズ: {os.path.getsize(OUTPUT_PATH):,} bytes")

if __name__ == "__main__":
    main()
