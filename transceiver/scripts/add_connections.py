#!/usr/bin/env python3
"""
PSN_TRX 配線追加スクリプト (KiCad 9 format対応)
ピンの実際の接続点 = (at x y angle) + length*(cos,sin) を正確に計算して
電源シンボルを追加する
"""
import re, uuid, os, math

SCH_PATH = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"

def gen_uuid():
    return str(uuid.uuid4())

def bracket_extract(text, start):
    depth, i = 0, start
    while i < len(text):
        if text[i] == '(':  depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return text[start:i+1]
        i += 1
    return text[start:]

# ============================================================
# lib_symbols からピン情報を抽出（接続点を正確に計算）
# ============================================================
def extract_pins(sym_text):
    """
    ピン根元座標 (at x y angle) + length*(cos,sin) = 実際の接続点
    """
    pins = []
    seen = set()  # (name, num) の重複を除外

    for m in re.finditer(
        r'\(pin\s+(\S+)\s+\S+\s*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)',
        sym_text
    ):
        ptype = m.group(1)
        px, py = float(m.group(2)), float(m.group(3))
        angle  = float(m.group(4))

        # length は (at...) の直後の行
        ctx_after = sym_text[m.end():m.end()+200]
        len_m = re.search(r'\(length\s+([-\d.]+)\)', ctx_after)
        length = float(len_m.group(1)) if len_m else 0.0

        # 実際の接続点を計算
        rad    = math.radians(angle)
        conn_x = round(px + length * math.cos(rad), 4)
        conn_y = round(py + length * math.sin(rad), 4)

        # ピン名・番号
        ctx = sym_text[m.start():m.start()+600]
        nm = re.search(r'\(name\s+"([^"]*)"', ctx)
        nu = re.search(r'\(number\s+"([^"]*)"', ctx)
        name = nm.group(1) if nm else ''
        num  = nu.group(1) if nu else ''

        # 同じピン番号の重複をスキップ
        key = (num, name)
        if key in seen:
            continue
        seen.add(key)

        pins.append({
            'type': ptype,
            'x': conn_x, 'y': conn_y,
            'name': name,
            'num':  num,
        })
    return pins

def parse_lib_symbols(sch_text):
    sym_pins = {}
    ls_pos = sch_text.find('\t(lib_symbols')
    if ls_pos < 0:
        ls_pos = sch_text.find('  (lib_symbols')
    if ls_pos < 0:
        ls_pos = sch_text.find('(lib_symbols')
    ls_text = bracket_extract(sch_text, ls_pos)

    for m in re.finditer(r'\(symbol\s+"([^"]+)"', ls_text):
        name = m.group(1)
        bare = name.split(':')[-1]
        if re.search(r'_\d+_\d+$', bare):
            continue
        sym_text = bracket_extract(ls_text, m.start())
        pins = extract_pins(sym_text)
        sym_pins[name] = pins
        print(f"  {name}: {len(pins)}pin  {[p['name'] or p['num'] for p in pins[:5]]}")
    return sym_pins

# ============================================================
# 配置済みシンボルを抽出
# ============================================================
def parse_placed(sch_text):
    comps = []
    for m in re.finditer(
        r'\(symbol\s*\n\s*\(lib_id\s+"([^"]+)"\)\s*\n\s*\(at\s+([-\d.]+)\s+([-\d.]+)',
        sch_text
    ):
        lib_id = m.group(1)
        x, y   = float(m.group(2)), float(m.group(3))
        ctx    = sch_text[m.start():m.start()+800]
        ref_m  = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', ctx)
        unit_m = re.search(r'\(unit\s+(\d+)\)', ctx)
        ref    = ref_m.group(1) if ref_m else '?'
        unit   = int(unit_m.group(1)) if unit_m else 1
        comps.append({'lib_id': lib_id, 'x': x, 'y': y, 'ref': ref, 'unit': unit})
    return comps

# ============================================================
# 電源ネット判定
# ============================================================
GND_NAMES = {'GND', 'VSS', '0', 'AGND', 'DGND', 'V-', 'V−'}

def net_for_pin(lib_id, ptype, pname, pnum, px, py):
    """ピン情報から接続ネットを返す。Noneなら未接続"""
    pname_up = pname.upper()

    # powerシンボル自体はスキップ
    if lib_id.startswith('power:'):
        return None

    sym = lib_id.split(':')[-1]

    # power_inタイプのピン名から判定
    if ptype == 'power_in':
        if pname_up in GND_NAMES or pname_up.startswith('GND') or pname_up == 'V-':
            return 'GND'
        if pname_up in ('+9V', '+9', 'VCC', 'VDD', 'V+', 'VI', 'VIN', 'IN'):
            if sym not in ('MC78L05_TO92',):  # 個別判定
                return '+9V'

    # BJT NPN
    if sym == 'Q_NPN_BCE':
        if pname_up == 'E':   return 'GND'
        if pname_up == 'C':   return None

    # BJT PNP
    if sym == 'Q_PNP_BCE':
        if pname_up == 'E':   return '+9V'
        if pname_up == 'C':   return None

    # N-ch JFET
    if sym == 'Q_NJFET_GDS':
        if pname_up == 'S':   return 'GND'

    # Dual-gate MOSFET 3SK263 (S=GND)
    if sym == '3SK263':
        if pname_up == 'S':   return 'GND'

    # Dual op-amp LM2904 power unit (unit3: pin4=V-, pin8=V+)
    if sym == 'LM2904':
        if pnum == '4':       return 'GND'
        if pnum == '8':       return '+9V'

    # Regulator MC78L05_TO92
    if sym == 'MC78L05_TO92':
        if pname_up == 'GND': return 'GND'
        if pname_up == 'VI':  return '+9V'
        if pname_up == 'VO':  return '+5V'

    return None

# ============================================================
# 要素生成
# ============================================================
def make_power_sym(net, x, y, ref_n):
    # GNDは回転0（標準向き：下向きシンボル）、+9V/+5Vも回転0（上向き）
    rot = 0
    return (
        f'\t(symbol\n'
        f'\t\t(lib_id "power:{net}")\n'
        f'\t\t(at {x:.4f} {y:.4f} {rot})\n'
        f'\t\t(unit 1)\n'
        f'\t\t(exclude_from_sim no)\n'
        f'\t\t(in_bom yes)\n'
        f'\t\t(on_board yes)\n'
        f'\t\t(dnp no)\n'
        f'\t\t(uuid "{gen_uuid()}")\n'
        f'\t\t(property "Reference" "#PWR{ref_n:03d}"\n'
        f'\t\t\t(at {x:.4f} {y:.4f} 0)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(hide yes)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Value" "{net}"\n'
        f'\t\t\t(at {x:.4f} {y:.4f} 0)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Footprint" ""\n'
        f'\t\t\t(at {x:.4f} {y:.4f} 0)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(hide yes)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t\t(property "Datasheet" ""\n'
        f'\t\t\t(at {x:.4f} {y:.4f} 0)\n'
        f'\t\t\t(effects\n'
        f'\t\t\t\t(font\n'
        f'\t\t\t\t\t(size 1.27 1.27)\n'
        f'\t\t\t\t)\n'
        f'\t\t\t\t(hide yes)\n'
        f'\t\t\t)\n'
        f'\t\t)\n'
        f'\t)'
    )

def make_lm2904_unit3(ref, x, y, ref_n_start):
    """LM2904のUnit3（電源ピン）プレースメントを追加"""
    # Unit3を少しオフセットした位置に配置（同位置でもOK）
    ux = round(x + 2.54, 4)
    uy = round(y, 4)
    sym_uuid = gen_uuid()
    return (
        f'  (symbol\n'
        f'    (lib_id "Amplifier_Operational:LM2904")\n'
        f'    (at {ux} {uy} 0)\n'
        f'    (unit 3)\n'
        f'    (exclude_from_sim no)\n'
        f'    (in_bom yes)\n'
        f'    (on_board yes)\n'
        f'    (dnp no)\n'
        f'    (fields_autoplaced yes)\n'
        f'    (uuid "{sym_uuid}")\n'
        f'    (property "Reference" "{ref}"\n'
        f'      (at {ux} {round(uy-2.5,4)} 0)\n'
        f'      (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'    (property "Value" "LM2904"\n'
        f'      (at {ux} {round(uy+2.5,4)} 0)\n'
        f'      (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'    (property "Footprint" ""\n'
        f'      (at {ux} {uy} 0)\n'
        f'      (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'    (property "Datasheet" ""\n'
        f'      (at {ux} {uy} 0)\n'
        f'\t  (effects (font (size 1.27 1.27)) (hide yes))\n'
        f'    )\n'
        f'  )'
    )

# ============================================================
# メイン
# ============================================================
def main():
    with open(SCH_PATH, encoding='utf-8') as f:
        sch_text = f.read()

    print("=== ピン位置解析 ===")
    sym_pins = parse_lib_symbols(sch_text)
    total_pins = sum(len(v) for v in sym_pins.values())
    print(f"  合計: {len(sym_pins)}シンボル, {total_pins}ピン")

    print("\n=== 配置部品解析 ===")
    comps = parse_placed(sch_text)
    print(f"  {len(comps)}部品")

    new_elems = []
    pwr_n = [1]
    stats = {'power': 0, 'skip': 0}
    lm2904_added = set()

    print("\n=== ネット接続生成 ===")
    for comp in comps:
        if comp['lib_id'].startswith('power:'):
            continue

        sym_name = comp['lib_id'].split(':')[-1]
        pins = sym_pins.get(comp['lib_id'], [])
        cx, cy = comp['x'], comp['y']

        # LM2904: Unit3（電源ピン）を追加配置
        if sym_name == 'LM2904' and comp['ref'] not in lm2904_added:
            lm2904_added.add(comp['ref'])
            new_elems.append(make_lm2904_unit3(comp['ref'], cx, cy, pwr_n[0]))
            print(f"  {comp['ref']}: Unit3追加 at ({cx+2.54:.4f},{cy:.4f})")
            # Unit3のピン座標でGND/+9Vを追加（unit3プレースメント位置基準）
            ux = cx + 2.54
            uy = cy
            # pin4(V-): lib_conn=(-2.54, -3.81) → sch_conn = ux-2.54, uy-(-3.81) = uy+3.81
            gnd_x = round(ux + (-2.54), 4)
            gnd_y = round(uy - (-3.81), 4)   # Y反転: cy - lib_y
            new_elems.append(make_power_sym('GND', gnd_x, gnd_y, pwr_n[0]))
            pwr_n[0] += 1
            stats['power'] += 1
            # pin8(V+): lib_conn=(-2.54, 3.81) → sch_conn = ux-2.54, uy-3.81
            vp_x = round(ux + (-2.54), 4)
            vp_y = round(uy - 3.81, 4)       # Y反転: cy - lib_y
            new_elems.append(make_power_sym('+9V', vp_x, vp_y, pwr_n[0]))
            pwr_n[0] += 1
            stats['power'] += 1
            continue

        for pin in pins:
            px = round(cx + pin['x'], 4)
            py = round(cy - pin['y'], 4)   # Y反転: ライブラリはY上向き、スケマティックはY下向き
            net = net_for_pin(comp['lib_id'], pin['type'], pin['name'], pin['num'], px, py)
            if net:
                new_elems.append(make_power_sym(net, px, py, pwr_n[0]))
                pwr_n[0] += 1
                stats['power'] += 1
                print(f"  {comp['ref']} pin{pin['num']}({pin['name']}): {net} at ({px},{py})")
            else:
                stats['skip'] += 1

    print(f"\n電源シンボル: {stats['power']}個")
    print(f"未割り当て:   {stats['skip']}個")

    # ファイル末尾の ")" の直前に挿入
    insert_pos = len(sch_text)
    for i in range(len(sch_text)-1, 0, -1):
        if sch_text[i] == ')' and sch_text[i-1] == '\n':
            insert_pos = i
            break

    new_sch = sch_text[:insert_pos] + '\n'.join(new_elems) + '\n' + sch_text[insert_pos:]

    with open(SCH_PATH, 'w', encoding='utf-8') as f:
        f.write(new_sch)

    print(f"\n完了: {SCH_PATH}")
    print(f"ファイルサイズ: {os.path.getsize(SCH_PATH):,} bytes")

if __name__ == "__main__":
    main()
