#!/usr/bin/env python3
"""
PSN_TRX KiCad 9.0 Schematic Generator
KiCadインストール済みライブラリからシンボル定義を読み込んで埋め込む
"""

import uuid
import re
import os

KICAD_SYM_DIR = r"C:\Program Files\KiCad\9.0\share\kicad\symbols"
OUTPUT_PATH   = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"

def gen_uuid():
    return str(uuid.uuid4())

# ============================================================
# 使用シンボル定義: (ライブラリファイル名, シンボル名)
# ============================================================
NEEDED_SYMBOLS = [
    ("Device",                  "R"),
    ("Device",                  "C"),
    ("Device",                  "L"),
    ("Device",                  "Crystal"),
    ("Device",                  "D"),
    ("Device",                  "LED"),
    ("Device",                  "Q_NJFET_GDS"),      # 2SK439用
    ("Transistor_BJT",          "Q_NPN_BCE"),
    ("Transistor_BJT",          "Q_PNP_BCE"),
    ("Transistor_FET",          "3SK263"),            # 3SK59代替（デュアルゲートMOSFET）
    ("Amplifier_Operational",   "LM2904"),            # NJM2904相当
    ("Regulator_Linear",        "MC78L05_TO92"),       # LP2950-5.0代替（extendsを回避）
    ("Switch",                  "SW_SPDT"),
    ("Switch",                  "SW_SPST"),
    ("Connector_Generic",       "Conn_01x02"),        # マイク用
    ("power",                   "GND"),
    ("power",                   "+9V"),
    ("power",                   "+5V"),
]

def extract_symbol(lib_path, sym_name):
    """
    .kicad_symファイルからシンボル定義を抽出する。
    ネストしたS式を正確に追跡する。
    """
    try:
        with open(lib_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"  [WARN] ライブラリ不在: {lib_path}")
        return None

    # シンボル開始位置を検索
    search = f'(symbol "{sym_name}"'
    pos = content.find(search)
    if pos == -1:
        # スペースなし形式も試す
        search2 = f"(symbol {sym_name} "
        pos = content.find(search2)
        if pos == -1:
            print(f"  [WARN] シンボル未発見: {sym_name} in {os.path.basename(lib_path)}")
            return None

    # ネスト追跡で対応する閉じ括弧を見つける
    depth = 0
    start = pos
    i = pos
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                return content[start:i+1]
        i += 1
    return None

def find_extends_parent(sym_text):
    """シンボルテキストからextendsの親シンボル名を取得する"""
    m = re.search(r'\(extends\s+"([^"]+)"', sym_text)
    return m.group(1) if m else None

def collect_lib_symbols(needed):
    """必要なシンボルをライブラリから収集する（extends親シンボルを再帰解決）"""
    collected = {}  # "Lib:Name" -> symbol_text
    queue = list(needed)
    visited = set()

    while queue:
        lib_name, sym_name = queue.pop(0)
        key = f"{lib_name}:{sym_name}"
        if key in visited:
            continue
        visited.add(key)

        lib_path = os.path.join(KICAD_SYM_DIR, f"{lib_name}.kicad_sym")
        sym_text = extract_symbol(lib_path, sym_name)
        if sym_text:
            collected[key] = sym_text
            print(f"  [OK] {key}")
            # extendsで親シンボルが必要な場合は同ライブラリから追加
            parent = find_extends_parent(sym_text)
            if parent and f"{lib_name}:{parent}" not in visited:
                print(f"       → extends親: {lib_name}:{parent}")
                queue.append((lib_name, parent))
        else:
            print(f"  [NG] {lib_name}:{sym_name}")
    return collected

# ============================================================
# 部品定義: (ref, value, lib:sym, block, description)
# ============================================================
COMPONENTS = [
    # --- 高周波増幅 (RF AMP) ---
    ("Q1",   "3SK59",         "Transistor_FET:3SK263",            "RF_AMP",   "高周波増幅 Dual-gate MOSFET"),
    ("R1",   "20k",           "Device:R",                          "RF_AMP",   ""),
    ("VR1",  "5k",            "Device:R",                          "RF_AMP",   "AGC VR"),
    ("R14",  "5k",            "Device:R",                          "RF_AMP",   ""),
    ("C1",   "15p",           "Device:C",                          "RF_AMP",   ""),
    ("C2",   "15p",           "Device:C",                          "RF_AMP",   ""),
    ("L1",   "7T50",          "Device:L",                          "RF_AMP",   "ハムバンドコイル"),
    ("L2",   "7T50",          "Device:L",                          "RF_AMP",   "ハムバンドコイル"),
    ("SW2",  "送受切替",       "Switch:SW_SPDT",                    "RF_AMP",   ""),

    # --- 検波 (DETECTOR) ---
    ("Q2",   "2SC1923",       "Transistor_BJT:Q_NPN_BCE",         "DETECTOR", "検波"),
    ("R2",   "1M",            "Device:R",                          "DETECTOR", ""),
    ("R21",  "4.7k",          "Device:R",                          "DETECTOR", ""),
    ("R3",   "1k",            "Device:R",                          "DETECTOR", ""),
    ("C3",   "0.001u",        "Device:C",                          "DETECTOR", ""),

    # --- 低周波増幅 (AF AMP) ---
    ("Q3",   "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "AF_AMP",   "1段"),
    ("Q4",   "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "AF_AMP",   "2段"),
    ("Q5",   "2SC2120",       "Transistor_BJT:Q_NPN_BCE",         "AF_AMP",   "出力NPN"),
    ("Q6",   "2SA950",        "Transistor_BJT:Q_PNP_BCE",         "AF_AMP",   "出力PNP"),
    ("R4",   "1.5k",          "Device:R",                          "AF_AMP",   ""),
    ("R5",   "1k",            "Device:R",                          "AF_AMP",   ""),
    ("R6",   "100k",          "Device:R",                          "AF_AMP",   ""),
    ("R7",   "1k",            "Device:R",                          "AF_AMP",   ""),
    ("R8",   "100k",          "Device:R",                          "AF_AMP",   ""),
    ("R9",   "1k",            "Device:R",                          "AF_AMP",   ""),
    ("R10",  "1k",            "Device:R",                          "AF_AMP",   ""),
    ("R11",  "10k",           "Device:R",                          "AF_AMP",   ""),
    ("R12",  "10k",           "Device:R",                          "AF_AMP",   ""),
    ("R15",  "100",           "Device:R",                          "AF_AMP",   ""),
    ("R43",  "330",           "Device:R",                          "AF_AMP",   ""),
    ("VR2",  "10k",           "Device:R",                          "AF_AMP",   "音量VR"),
    ("C4",   "0.1u",          "Device:C",                          "AF_AMP",   ""),
    ("C5",   "10u",           "Device:C",                          "AF_AMP",   ""),
    ("C6",   "0.1u",          "Device:C",                          "AF_AMP",   ""),
    ("C7",   "0.1u",          "Device:C",                          "AF_AMP",   ""),
    ("C28",  "100u",          "Device:C",                          "AF_AMP",   ""),
    ("C29",  "1u",            "Device:C",                          "AF_AMP",   ""),

    # --- VXO ---
    ("Q7",   "2SC1923",       "Transistor_BJT:Q_NPN_BCE",         "VXO",      "VXO増幅"),
    ("Q8",   "2SC1923",       "Transistor_BJT:Q_NPN_BCE",         "VXO",      "VXO発振"),
    ("X1",   "50.5MHz/3",     "Device:Crystal",                    "VXO",      "水晶振動子"),
    ("TC1",  "40p",           "Device:C",                          "VXO",      "トリマ"),
    ("TC2",  "5p",            "Device:C",                          "VXO",      "トリマ"),
    ("TC3",  "30p",           "Device:C",                          "VXO",      "トリマ"),
    ("C10",  "100p",          "Device:C",                          "VXO",      ""),
    ("C11",  "47p",           "Device:C",                          "VXO",      ""),
    ("C12",  "47p",           "Device:C",                          "VXO",      ""),
    ("C13",  "5p",            "Device:C",                          "VXO",      ""),
    ("C14",  "4p",            "Device:C",                          "VXO",      ""),
    ("C17",  "15p",           "Device:C",                          "VXO",      ""),
    ("C25",  "10u",           "Device:C",                          "VXO",      ""),
    ("R17",  "100k",          "Device:R",                          "VXO",      ""),
    ("R16",  "10k",           "Device:R",                          "VXO",      ""),
    ("R18",  "1k",            "Device:R",                          "VXO",      ""),
    ("R19",  "220k",          "Device:R",                          "VXO",      ""),
    ("L3",   "7T5",           "Device:L",                          "VXO",      ""),
    ("L4",   "T-30-10",       "Device:L",                          "VXO",      "0.4mmホルマル線6回"),
    ("L5",   "T-30-10",       "Device:L",                          "VXO",      "Link1回"),

    # --- RF PSN ---
    ("Q9",   "2SK439",        "Device:Q_NJFET_GDS",       "RF_PSN",   "RF移相器"),
    ("Q10",  "2SK439",        "Device:Q_NJFET_GDS",       "RF_PSN",   "RF移相器"),
    ("L6",   "7T50",          "Device:L",                          "RF_PSN",   ""),
    ("L7",   "7T50",          "Device:L",                          "RF_PSN",   ""),
    ("C16",  "15p",           "Device:C",                          "RF_PSN",   ""),
    ("C18",  "15p",           "Device:C",                          "RF_PSN",   ""),
    ("R20",  "100k",          "Device:R",                          "RF_PSN",   ""),
    ("R42",  "100k",          "Device:R",                          "RF_PSN",   ""),
    ("R51",  "51",            "Device:R",                          "RF_PSN",   ""),
    ("R52",  "51",            "Device:R",                          "RF_PSN",   ""),

    # --- 平衡変調 (BALANCED MOD) ---
    ("D1",   "1N60",          "Device:D",                          "BAL_MOD",  "平衡変調"),
    ("D2",   "1N60",          "Device:D",                          "BAL_MOD",  "平衡変調"),
    ("D3",   "1N60",          "Device:D",                          "BAL_MOD",  "平衡変調"),
    ("D4",   "1N60",          "Device:D",                          "BAL_MOD",  "平衡変調"),
    ("L8",   "15mH",          "Device:L",                          "BAL_MOD",  "AF変成器"),
    ("L9",   "1mH",           "Device:L",                          "BAL_MOD",  ""),
    ("L10",  "1mH",           "Device:L",                          "BAL_MOD",  ""),
    ("L11",  "7T50",          "Device:L",                          "BAL_MOD",  "合成コイル"),
    ("L12",  "7T50",          "Device:L",                          "BAL_MOD",  ""),
    ("L13",  "7T50",          "Device:L",                          "BAL_MOD",  ""),
    ("C19",  "33p",           "Device:C",                          "BAL_MOD",  ""),
    ("C20",  "0.001u",        "Device:C",                          "BAL_MOD",  ""),
    ("C21",  "0.001u",        "Device:C",                          "BAL_MOD",  ""),
    ("R29",  "4.7k",          "Device:R",                          "BAL_MOD",  ""),
    ("R31",  "1M",            "Device:R",                          "BAL_MOD",  ""),
    ("R32",  "4.7k",          "Device:R",                          "BAL_MOD",  ""),
    ("R33",  "22",            "Device:R",                          "BAL_MOD",  ""),
    ("R34",  "100",           "Device:R",                          "BAL_MOD",  ""),
    ("R35",  "100k",          "Device:R",                          "BAL_MOD",  ""),
    ("VR4",  "1k",            "Device:R",                          "BAL_MOD",  "キャリア調整"),
    ("VR5",  "1k",            "Device:R",                          "BAL_MOD",  ""),
    ("Q13",  "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "BAL_MOD",  ""),

    # --- AF PSN・信号分割 ---
    ("IC2",  "NJM2904",       "Amplifier_Operational:LM2904",    "AF_PSN",   "AF PSN"),
    ("Q12",  "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "AF_PSN",   ""),
    ("R25",  "10k",           "Device:R",                          "AF_PSN",   ""),
    ("R26",  "10k",           "Device:R",                          "AF_PSN",   ""),
    ("R27",  "10k",           "Device:R",                          "AF_PSN",   ""),
    ("R28",  "1k",            "Device:R",                          "AF_PSN",   ""),
    ("VR3",  "10k",           "Device:R",                          "AF_PSN",   "位相調整"),
    ("C15",  "10u",           "Device:C",                          "AF_PSN",   ""),
    ("R30",  "22",            "Device:R",                          "AF_PSN",   ""),

    # --- マイクアンプ (MIC AMP) ---
    ("Q11",  "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "MIC_AMP",  "マイクアンプ"),
    ("R22",  "100k",          "Device:R",                          "MIC_AMP",  ""),
    ("R23",  "100k",          "Device:R",                          "MIC_AMP",  ""),
    ("R24",  "1k",            "Device:R",                          "MIC_AMP",  ""),
    ("R25b", "330",           "Device:R",                          "MIC_AMP",  ""),
    ("C16b", "0.1u",          "Device:C",                          "MIC_AMP",  ""),
    ("MIC1", "MIC",           "Connector_Generic:Conn_01x02",           "MIC_AMP",  ""),

    # --- 励振増幅 (DRIVER) ---
    ("Q14",  "2SK439",        "Device:Q_NJFET_GDS",       "DRIVER",   "励振増幅"),
    ("R36",  "51",            "Device:R",                          "DRIVER",   ""),
    ("R46",  "51",            "Device:R",                          "DRIVER",   ""),
    ("C23",  "15p",           "Device:C",                          "DRIVER",   ""),
    ("C24",  "15p",           "Device:C",                          "DRIVER",   ""),

    # --- 終段増幅 (FINAL AMP) ---
    ("Q15",  "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "FINAL",    "終段増幅"),
    ("Q16",  "2SC1815",       "Transistor_BJT:Q_NPN_BCE",         "FINAL",    "終段増幅"),
    ("D5",   "1N60",          "Device:D",                          "FINAL",    ""),
    ("D6",   "1N60",          "Device:D",                          "FINAL",    ""),
    ("R37",  "20k",           "Device:R",                          "FINAL",    ""),
    ("R38",  "4.7k",          "Device:R",                          "FINAL",    ""),
    ("R39",  "51",            "Device:R",                          "FINAL",    ""),
    ("R40",  "1k",            "Device:R",                          "FINAL",    ""),
    ("R41",  "100",           "Device:R",                          "FINAL",    ""),
    ("L14",  "T-50-10",       "Device:L",                          "FINAL",    "0.4mmホルマル線18回"),
    ("L15",  "T-50-10",       "Device:L",                          "FINAL",    "0.4mmホルマル線18回"),
    ("L13b", "7T50",          "Device:L",                          "FINAL",    ""),
    ("C26",  "15p",           "Device:C",                          "FINAL",    ""),
    ("C27",  "5p",            "Device:C",                          "FINAL",    ""),
    ("LED2", "LED黄",          "Device:LED",                        "FINAL",    "送信表示"),

    # --- 電源 (POWER) ---
    ("IC1",  "LP2950L-5.0V",  "Regulator_Linear:MC78L05_TO92",          "POWER",    "5V安定化"),
    ("C8",   "10u",           "Device:C",                          "POWER",    "入力"),
    ("C8b",  "10u",           "Device:C",                          "POWER",    "出力"),
    ("R13",  "1k",            "Device:R",                          "POWER",    ""),
    ("LED1", "LED",           "Device:LED",                        "POWER",    "電源表示"),
    ("SW1",  "SW",            "Switch:SW_SPST",                    "POWER",    "電源SW"),
]

# ============================================================
# ブロック配置原点 (mm)
# ============================================================
# 全座標を2.54mm(100mil)グリッドの倍数に統一
_U = 2.54  # 1グリッド単位

BLOCK_ORIGINS = {
    "RF_AMP":   (  8*_U,  10*_U),   # 20.32,  25.40
    "DETECTOR": ( 44*_U,  10*_U),   #111.76,  25.40
    "AF_AMP":   ( 78*_U,  10*_U),   #198.12,  25.40
    "POWER":    (120*_U,  10*_U),   #304.80,  25.40
    "FINAL":    (  8*_U,  50*_U),   # 20.32, 127.00
    "DRIVER":   (  8*_U,  78*_U),   # 20.32, 198.12
    "RF_PSN":   ( 44*_U,  50*_U),   #111.76, 127.00
    "BAL_MOD":  ( 44*_U,  78*_U),   #111.76, 198.12
    "VXO":      ( 78*_U,  50*_U),   #198.12, 127.00
    "AF_PSN":   ( 78*_U,  86*_U),   #198.12, 218.44
    "MIC_AMP":  (120*_U,  78*_U),   #304.80, 198.12
}

GRID_X = 5*_U   # 12.70mm (5×2.54)
GRID_Y = 6*_U   # 15.24mm (6×2.54)
COLS   = 5    # 1行あたり最大部品数

BLOCK_LABELS = {
    "RF_AMP":   "高周波増幅",
    "DETECTOR": "検波",
    "AF_AMP":   "低周波増幅",
    "VXO":      "VXO",
    "RF_PSN":   "RF PSN",
    "BAL_MOD":  "平衡変調・合成",
    "AF_PSN":   "AF PSN・信号分割",
    "MIC_AMP":  "マイクアンプ",
    "DRIVER":   "励振増幅",
    "FINAL":    "終段増幅",
    "POWER":    "電源",
}

def mm(v):
    return round(float(v), 4)

def place_components(components):
    placed = []
    counters = {}
    for ref, value, lib_sym, block, desc in components:
        idx = counters.get(block, 0)
        ox, oy = BLOCK_ORIGINS[block]
        col = idx % COLS
        row = idx // COLS
        x = mm(ox + col * GRID_X)
        y = mm(oy + row * GRID_Y)
        counters[block] = idx + 1
        placed.append({
            "ref": ref, "value": value, "lib_sym": lib_sym,
            "block": block, "desc": desc,
            "x": x, "y": y,
            "uuid": gen_uuid(),
        })
    return placed, counters

def sym_entry(lib_sym_text, lib_name, sym_name, all_lib_map):
    """lib_symbols内のエントリとして整形（インデント付き）"""
    new_name = f"{lib_name}:{sym_name}"
    # 先頭の (symbol "OriginalName" を置換
    result = re.sub(
        r'^\(symbol\s+"[^"]*"',
        f'(symbol "{new_name}"',
        lib_sym_text,
        count=1
    )
    # extends の参照先も "Lib:Name" 形式に書き換える
    def fix_extends(m):
        parent_bare = m.group(1)
        # all_lib_mapから対応するライブラリを探す
        for (lname, sname), _ in all_lib_map.items():
            if sname == parent_bare:
                return f'(extends "{lname}:{parent_bare}")'
        return m.group(0)  # 見つからなければそのまま
    result = re.sub(r'\(extends\s+"([^"]+)"\)', fix_extends, result)
    # 各行に2スペースインデント
    indented = "\n".join("  " + line for line in result.splitlines())
    return indented

def write_component(p):
    lib_sym = p["lib_sym"]
    x, y = p["x"], p["y"]
    lines = [
        f'  (symbol',
        f'    (lib_id "{lib_sym}")',
        f'    (at {x} {y} 0)',
        f'    (unit 1)',
        f'    (exclude_from_sim no)',
        f'    (in_bom yes)',
        f'    (on_board yes)',
        f'    (dnp no)',
        f'    (fields_autoplaced yes)',
        f'    (uuid "{p["uuid"]}")',
        f'    (property "Reference" "{p["ref"]}"',
        f'      (at {x} {mm(y-2.5)} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
        f'    (property "Value" "{p["value"]}"',
        f'      (at {x} {mm(y+2.5)} 0)',
        f'      (effects (font (size 1.27 1.27)))',
        f'    )',
        f'    (property "Footprint" ""',
        f'      (at {x} {y} 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes))',
        f'    )',
        f'    (property "Datasheet" ""',
        f'      (at {x} {y} 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes))',
        f'    )',
    ]
    if p["desc"]:
        lines += [
            f'    (property "ki_description" "{p["desc"]}"',
            f'      (at {x} {y} 0)',
            f'      (effects (font (size 1.27 1.27)) (hide yes))',
            f'    )',
        ]
    lines.append(f'  )')
    return "\n".join(lines)

def write_block_rect_and_label(block, ox, oy, num_comp):
    cols = min(num_comp, COLS)
    rows = max(1, (num_comp + COLS - 1) // COLS)
    x1 = mm(ox - 4)
    y1 = mm(oy - 8)
    x2 = mm(ox + cols * GRID_X + 2)
    y2 = mm(oy + rows * GRID_Y + 2)
    label = BLOCK_LABELS.get(block, block)
    out = []
    out.append(
        f'  (rectangle (start {x1} {y1}) (end {x2} {y2})\n'
        f'    (stroke (width 0.2) (type default))\n'
        f'    (fill (type none))\n'
        f'    (uuid "{gen_uuid()}")\n'
        f'  )'
    )
    out.append(
        f'  (text "{label}"\n'
        f'    (at {mm(ox)} {mm(oy-5)} 0)\n'
        f'    (effects (font (size 2.54 2.54) bold))\n'
        f'    (uuid "{gen_uuid()}")\n'
        f'  )'
    )
    return "\n".join(out)

def main():
    print("=== KiCadシンボルライブラリ読み込み ===")
    lib_syms_collected = {}
    for lib_name, sym_name in NEEDED_SYMBOLS:
        lib_path = os.path.join(KICAD_SYM_DIR, f"{lib_name}.kicad_sym")
        sym_text = extract_symbol(lib_path, sym_name)
        if sym_text:
            key = f"{lib_name}:{sym_name}"
            lib_syms_collected[key] = (sym_text, lib_name, sym_name)
            print(f"  [OK] {key}")
        else:
            print(f"  [NG] {lib_name}:{sym_name}")

    print("\n=== 部品配置計算 ===")
    placed, counters = place_components(COMPONENTS)
    print(f"  総部品数: {len(placed)}")

    print("\n=== .kicad_sch 生成 ===")
    lines = []
    lines.append("(kicad_sch")
    lines.append("  (version 20241209)")
    lines.append('  (generator "PSN_TRX_generator")')
    lines.append('  (generator_version "9.0")')
    lines.append('  (paper "A1")')
    lines.append("")

    # lib_symbols セクション
    # all_lib_map: {(lib_name, sym_name): sym_text} — extends解決に使用
    all_lib_map = {(lib_name, sym_name): sym_text
                   for key, (sym_text, lib_name, sym_name) in lib_syms_collected.items()}
    lines.append("  (lib_symbols")
    for key, (sym_text, lib_name, sym_name) in lib_syms_collected.items():
        entry = sym_entry(sym_text, lib_name, sym_name, all_lib_map)
        lines.append(entry)
    lines.append("  )")
    lines.append("")

    # ブロック枠・ラベル
    for block, (ox, oy) in BLOCK_ORIGINS.items():
        cnt = counters.get(block, 0)
        if cnt > 0:
            lines.append(write_block_rect_and_label(block, ox, oy, cnt))
    lines.append("")

    # 部品配置
    for p in placed:
        lines.append(write_component(p))
        lines.append("")

    lines.append(")")

    content = "\n".join(lines)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n生成完了: {OUTPUT_PATH}")
    print(f"ファイルサイズ: {os.path.getsize(OUTPUT_PATH):,} bytes")

if __name__ == "__main__":
    main()
