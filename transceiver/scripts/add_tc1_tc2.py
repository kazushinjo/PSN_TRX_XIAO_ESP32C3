#!/usr/bin/env python3
"""
add_tc1_tc2.py
1. 重複C13(40p)を削除（uuid: 82d5c981-6f52-443b-aa51-44d1efbf86e9）
2. lib_symbols に Device:C_Variable を追加
3. TC1(40p) / TC2(5p) を Device:C_Variable + フットプリント付きで追加
"""

import uuid
import re

SCH_PATH = r"C:\Users\kazus\KiCad\PSN_TRX\PSN_TRX.kicad_sch"
SYM_LIB  = r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Device.kicad_sym"

# ============================================================
# 定数
# ============================================================
REMOVE_UUID = "82d5c981-6f52-443b-aa51-44d1efbf86e9"   # C13(40p) 重複

FOOTPRINT = "PSN_TRX:C_Trimmer_TMCV01"
SCH_UUID  = "50835569-93ad-4c8c-aafc-424a6a3761ef"      # 回路図UUID

def gen_uuid():
    return str(uuid.uuid4())

def mm(v):
    return round(float(v), 4)

# ============================================================
# Device:C_Variable を Device.kicad_sym から抽出し、
# schematic lib_symbols 用にインデントを +1 タブ調整
# ============================================================
def extract_c_variable(sym_lib_path):
    with open(sym_lib_path, "r", encoding="utf-8") as f:
        content = f.read()

    # '(symbol "C_Variable"\n' を検索
    marker = '\t(symbol "C_Variable"\n'
    idx = content.find(marker)
    if idx == -1:
        raise RuntimeError("C_Variable が Device.kicad_sym に見つかりません")

    # 対応する閉じ括弧まで抽出
    depth = 0
    i = idx
    while i < len(content):
        if content[i] == '(':
            depth += 1
        elif content[i] == ')':
            depth -= 1
            if depth == 0:
                block = content[idx:i+1]
                break
        i += 1

    # 名前を Device:C_Variable に変更
    block = block.replace('(symbol "C_Variable"', '(symbol "Device:C_Variable"', 1)

    # 各行に 1 タブ追加（lib_symbols の深さに合わせる）
    lines = block.split('\n')
    indented = '\n'.join('\t' + line for line in lines)

    return indented

# ============================================================
# シンボルブロック生成（Device:C_Variable 用）
# ============================================================
def c_variable(ref, value, x, y, rot=0, footprint=FOOTPRINT, desc=""):
    u = gen_uuid()
    x_ref  = mm(x)
    y_ref  = mm(y - 3.81)
    x_val  = mm(x)
    y_val  = mm(y + 3.81)

    fp_hide = "(hide yes)" if not footprint else "(hide yes)"  # 常に非表示

    lines = [
        f'\t(symbol',
        f'\t\t(lib_id "Device:C_Variable")',
        f'\t\t(at {mm(x)} {mm(y)} {rot})',
        f'\t\t(unit 1)',
        f'\t\t(body_style 1)',
        f'\t\t(exclude_from_sim no)',
        f'\t\t(in_bom yes)',
        f'\t\t(on_board yes)',
        f'\t\t(in_pos_files yes)',
        f'\t\t(dnp no)',
        f'\t\t(fields_autoplaced yes)',
        f'\t\t(uuid "{u}")',
        f'\t\t(property "Reference" "{ref}"',
        f'\t\t\t(at {x_ref} {y_ref} 0)',
        f'\t\t\t(show_name no)',
        f'\t\t\t(do_not_autoplace no)',
        f'\t\t\t(effects',
        f'\t\t\t\t(font',
        f'\t\t\t\t\t(size 1.27 1.27)',
        f'\t\t\t\t)',
        f'\t\t\t)',
        f'\t\t)',
        f'\t\t(property "Value" "{value}"',
        f'\t\t\t(at {x_val} {y_val} 0)',
        f'\t\t\t(show_name no)',
        f'\t\t\t(do_not_autoplace no)',
        f'\t\t\t(effects',
        f'\t\t\t\t(font',
        f'\t\t\t\t\t(size 1.27 1.27)',
        f'\t\t\t\t)',
        f'\t\t\t)',
        f'\t\t)',
        f'\t\t(property "Footprint" "{footprint}"',
        f'\t\t\t(at {mm(x)} {mm(y)} 0)',
        f'\t\t\t(hide yes)',
        f'\t\t\t(show_name no)',
        f'\t\t\t(do_not_autoplace no)',
        f'\t\t\t(effects',
        f'\t\t\t\t(font',
        f'\t\t\t\t\t(size 1.27 1.27)',
        f'\t\t\t\t)',
        f'\t\t\t)',
        f'\t\t)',
        f'\t\t(property "Datasheet" ""',
        f'\t\t\t(at {mm(x)} {mm(y)} 0)',
        f'\t\t\t(hide yes)',
        f'\t\t\t(show_name no)',
        f'\t\t\t(do_not_autoplace no)',
        f'\t\t\t(effects',
        f'\t\t\t\t(font',
        f'\t\t\t\t\t(size 1.27 1.27)',
        f'\t\t\t\t)',
        f'\t\t\t)',
        f'\t\t)',
    ]
    if desc:
        lines += [
            f'\t\t(property "ki_description" "{desc}"',
            f'\t\t\t(at {mm(x)} {mm(y)} 0)',
            f'\t\t\t(hide yes)',
            f'\t\t\t(show_name no)',
            f'\t\t\t(do_not_autoplace no)',
            f'\t\t\t(effects',
            f'\t\t\t\t(font',
            f'\t\t\t\t\t(size 1.27 1.27)',
            f'\t\t\t\t)',
            f'\t\t\t)',
            f'\t\t)',
        ]
    lines += [
        f'\t\t(pin "1"',
        f'\t\t\t(uuid "{gen_uuid()}")',
        f'\t\t)',
        f'\t\t(pin "2"',
        f'\t\t\t(uuid "{gen_uuid()}")',
        f'\t\t)',
        f'\t\t(instances',
        f'\t\t\t(project "PSN_TRX"',
        f'\t\t\t\t(path "/{SCH_UUID}"',
        f'\t\t\t\t\t(reference "{ref}")',
        f'\t\t\t\t\t(unit 1)',
        f'\t\t\t\t)',
        f'\t\t\t)',
        f'\t\t)',
        f'\t)',
    ]
    return '\n'.join(lines)

# ============================================================
# ブロック削除（UUID指定）
# ============================================================
def remove_symbol_by_uuid(content, target_uuid):
    """指定UUIDを含む (symbol ...) ブロックを削除する"""
    # \t(symbol\n を検索してブロック抽出→UUID チェック→削除
    result = []
    i = 0
    removed = 0

    while i < len(content):
        if content[i:i+9] == '\t(symbol\n':
            # ブロック開始
            start = i
            depth = 0
            j = i
            while j < len(content):
                if content[j] == '(':
                    depth += 1
                elif content[j] == ')':
                    depth -= 1
                    if depth == 0:
                        block_end = j + 1
                        break
                j += 1

            block = content[start:block_end]
            if target_uuid in block:
                print(f"  → 削除: UUID={target_uuid} のブロック ({block_end-start} chars)")
                removed += 1
                # 直後の \n も除去
                i = block_end
                if i < len(content) and content[i] == '\n':
                    i += 1
                continue
            else:
                result.append(block)
                i = block_end
        else:
            result.append(content[i])
            i += 1

    return ''.join(result), removed

# ============================================================
# メイン処理
# ============================================================
def main():
    with open(SCH_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"読み込み完了: {len(content):,} chars")

    # --- 1. C13(40p) 重複削除 ---
    print("\n[1] C13(40p) 重複ブロック削除...")
    content, n = remove_symbol_by_uuid(content, REMOVE_UUID)
    if n == 0:
        print("  → 対象ブロックが見つかりません（既に削除済みか UUID が変わっています）")
    else:
        print(f"  → {n} 個削除しました")

    # --- 2. Device:C_Variable を lib_symbols に追加 ---
    print("\n[2] Device:C_Variable を lib_symbols に追加...")
    if '"Device:C_Variable"' in content:
        print("  → 既に存在するためスキップ")
    else:
        c_var_def = extract_c_variable(SYM_LIB)
        # lib_symbols の閉じ \t) の直前に挿入
        # lib_symbols 内の最後の (embedded_fonts no) の後の \t\t)\n\t)\n を探す
        # より確実に: (lib_symbols ... の対応する \t) を探す
        lib_sym_start = content.find('\t(lib_symbols\n')
        if lib_sym_start == -1:
            print("ERROR: lib_symbols が見つかりません")
            return
        # lib_symbols の閉じ括弧を探す（深さトラッキング）
        depth = 0
        i = lib_sym_start
        lib_sym_end = -1
        while i < len(content):
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
                if depth == 0:
                    lib_sym_end = i  # この ) の直前に挿入
                    break
            i += 1
        if lib_sym_end == -1:
            print("ERROR: lib_symbols の終端が見つかりません")
            return

        insert_pos = lib_sym_end  # \t) の ( 位置
        content = content[:insert_pos] + c_var_def + '\n\t' + content[insert_pos:]
        print("  → 追加しました")

    # --- 3. TC1・TC2 コンポーネント追加 ---
    print("\n[3] TC1(40p) / TC2(5p) を追加...")

    # 既に存在するか確認
    existing_tc = re.findall(r'reference "TC[12]"', content)
    if existing_tc:
        print(f"  → 既に存在します: {existing_tc}")
        print("     重複を避けるため追加をスキップします")
    else:
        tc1 = c_variable("TC1", "40p", 629.92, 214.63, desc="VXOトリマ40p")
        tc2 = c_variable("TC2", "5p",  614.68, 214.63, desc="VXOトリマ5p")
        adds = '\n' + tc1 + '\n\n' + tc2 + '\n'

        # 末尾の \n) の直前に挿入
        last = content.rfind('\n)')
        content = content[:last] + adds + content[last:]
        print(f"  → TC1 at (629.92, 214.63)")
        print(f"  → TC2 at (614.68, 214.63)")

    # --- 書き出し ---
    with open(SCH_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"\n完了: {SCH_PATH}")
    print(f"ファイルサイズ: {len(content):,} chars")
    print("\nKiCadでファイルを開き直して確認してください。")

if __name__ == "__main__":
    main()
