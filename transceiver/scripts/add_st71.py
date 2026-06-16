#!/usr/bin/env python3
"""
add_st71.py
L8 (ST-71音声トランス) を ST-71 の実体に合わせて変更する。

  - reference : L8 -> T1            (コイル L ではなくトランス T)
  - value     : 15mH -> ST-71
  - symbol    : Device:Transformer_1P_1S -> Device:Transformer_1P_SS
                (二次センタータップ付き。AF PSN 信号分割用)
  - footprint : "" -> PSN_TRX:Transformer_ST71_CB19

対象シンボルは uuid で特定する。Device:Transformer_1P_SS の定義は
Device.kicad_sym から抽出し lib_symbols に追加する(無ければ)。
"""
import uuid
import re

SCH    = r"C:\Users\shinjo\OneDrive\デスクトップ\KiCad\PSN_TRX\PSN_TRX.kicad_sch"
SYMLIB = r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Device.kicad_sym"

L8_UUID   = "6c85fe36-55c4-4d74-babd-32413bd95c2a"
NEW_REF   = "T1"
NEW_VAL   = "ST-71"
NEW_FP    = "PSN_TRX:Transformer_ST71_CB19"
NEW_LIBID = "Device:Transformer_1P_SS"
SYM_NAME  = "Transformer_1P_SS"
NEW_PINS  = ["1", "2", "3", "4", "5"]   # 1,2=一次  3,5=二次端  4=二次CT


def gen_uuid():
    return str(uuid.uuid4())


def balanced_block(content, start):
    """content[start] が '(' の位置。対応する ')' までの [start, end) を返す。"""
    depth = 0
    i = start
    while i < len(content):
        c = content[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return start, i + 1
        i += 1
    raise RuntimeError("括弧が閉じていません")


def extract_symbol(libpath, name):
    """ライブラリから (symbol "name" ...) を抽出し Device:name にリネーム、+1タブ。"""
    with open(libpath, encoding="utf-8") as f:
        content = f.read()
    marker = f'\t(symbol "{name}"\n'
    idx = content.find(marker)
    if idx == -1:
        raise RuntimeError(f"{name} が {libpath} に見つかりません")
    s, e = balanced_block(content, idx)        # idx は '\t' なので () 探索は idx+1 から
    # idx は '\t'。'(' は idx+1
    s, e = balanced_block(content, content.index('(', idx))
    block = content[s:e]
    block = block.replace(f'(symbol "{name}"', f'(symbol "Device:{name}"', 1)
    return '\n'.join('\t' + ln for ln in block.split('\n'))


def main():
    with open(SCH, encoding="utf-8") as f:
        content = f.read()
    print(f"読み込み: {len(content):,} chars")

    # --- 1. lib_symbols に Device:Transformer_1P_SS を追加 ---
    if f'"{NEW_LIBID}"' in content:
        print(f"[1] {NEW_LIBID} は既に lib_symbols 内。スキップ")
    else:
        sym_def = extract_symbol(SYMLIB, SYM_NAME)
        ls = content.find('\t(lib_symbols\n')
        if ls == -1:
            raise RuntimeError("lib_symbols が見つかりません")
        s, e = balanced_block(content, content.index('(', ls))
        ins = e - 1            # 最後の ')' の直前 (この行は '\t)')
        # '\t)' の '\t' の前に挿入したいので行頭を探す
        line_start = content.rfind('\n', 0, ins) + 1
        content = content[:line_start] + sym_def + '\n' + content[line_start:]
        print(f"[1] {NEW_LIBID} を lib_symbols に追加 ({len(sym_def)} chars)")

    # --- 2. 対象シンボルブロックを uuid で特定 ---
    upos = content.find(f'(uuid "{L8_UUID}")')
    if upos == -1:
        raise RuntimeError(f"uuid {L8_UUID} が見つかりません")
    # 後方へ '\t(symbol\n' を探す
    bstart = content.rfind('\t(symbol\n', 0, upos)
    if bstart == -1:
        raise RuntimeError("シンボルブロック先頭が見つかりません")
    s, e = balanced_block(content, content.index('(', bstart))
    block = content[s:e]
    orig_block = block

    # --- 3. ブロック内を書き換え ---
    assert block.count('(lib_id "Device:Transformer_1P_1S")') == 1
    block = block.replace('(lib_id "Device:Transformer_1P_1S")',
                          f'(lib_id "{NEW_LIBID}")', 1)

    assert block.count('(property "Reference" "L8"') == 1
    block = block.replace('(property "Reference" "L8"',
                          f'(property "Reference" "{NEW_REF}"', 1)

    assert block.count('(property "Value" "15mH"') == 1
    block = block.replace('(property "Value" "15mH"',
                          f'(property "Value" "{NEW_VAL}"', 1)

    assert block.count('(property "Footprint" ""') == 1
    block = block.replace('(property "Footprint" ""',
                          f'(property "Footprint" "{NEW_FP}"', 1)

    assert block.count('(reference "L8")') == 1
    block = block.replace('(reference "L8")', f'(reference "{NEW_REF}")', 1)

    # --- 4. ピンを 1..5 に差し替え ---
    new_pin_txt = ''.join(
        f'\t\t(pin "{n}"\n\t\t\t(uuid "{gen_uuid()}")\n\t\t)\n'
        for n in NEW_PINS
    )
    # 最初の '\t\t(pin "' から '\t\t(instances' 直前まで
    m1 = re.search(r'\t\t\(pin "', block)
    m2 = re.search(r'\t\t\(instances', block)
    if not (m1 and m2):
        raise RuntimeError("pin / instances 領域が見つかりません")
    block = block[:m1.start()] + new_pin_txt + block[m2.start():]

    content = content[:s] + block + content[e:]
    print("[2-4] シンボル書き換え完了 (lib_id / ref / value / footprint / pins)")

    # --- 5. 括弧バランス検証 ---
    if content.count('(') != content.count(')'):
        raise RuntimeError(
            f"括弧不一致! ( = {content.count('(')} , ) = {content.count(')')}")
    print(f"[5] 括弧バランスOK ( {content.count('(')} 対 )")

    with open(SCH, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"書き出し完了: {len(content):,} chars")
    print("KiCad で開き直して確認してください。")


if __name__ == "__main__":
    main()
