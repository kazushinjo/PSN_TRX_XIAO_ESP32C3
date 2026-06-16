"""
L11のシンボルをTransformer_1P_1S -> Transformer_1P_2Sに変更するスクリプト。
1. lib_symbolsにTransformer_1P_2Sを追加
2. L11のlib_idを変更
3. L11インスタンスにpin 5, 6を追加
"""
import re
import uuid

SCH = r"C:\Users\kazus\KiCad\PSN_TRX_New\PSN_TRX.kicad_sch"
LIB = r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Device.kicad_sym"

# --- Device.kicad_sym から Transformer_1P_2S を抽出 ---
with open(LIB, "r", encoding="utf-8") as f:
    lib_text = f.read()

# トップレベルの (symbol "Transformer_1P_2S" ...) を取得
start = lib_text.index('\t(symbol "Transformer_1P_2S"')
# 次のトップレベルシンボルを探す
end = lib_text.index('\n\t(symbol "', start + 1)
sym_raw = lib_text[start:end]  # \t(symbol "Transformer_1P_2S" ... )

# lib_symbols内のインデントは3タブ → 元が1タブなので2タブ追加
lines = sym_raw.split("\n")
indented_lines = []
for line in lines:
    if line == "":
        indented_lines.append("")
    else:
        indented_lines.append("\t\t" + line)
sym_indented = "\n".join(indented_lines)

# Device: プレフィックスを付けてシンボル名を変更
sym_indented = sym_indented.replace(
    '\t\t\t(symbol "Transformer_1P_2S"',
    '\t\t\t(symbol "Device:Transformer_1P_2S"'
)
sym_indented = sym_indented.replace(
    '\t\t\t(symbol "Transformer_1P_2S_0_1"',
    '\t\t\t(symbol "Transformer_1P_2S_0_1"'
)
sym_indented = sym_indented.replace(
    '\t\t\t(symbol "Transformer_1P_2S_1_1"',
    '\t\t\t(symbol "Transformer_1P_2S_1_1"'
)

# --- 回路図を読み込む ---
with open(SCH, "r", encoding="utf-8") as f:
    sch = f.read()

# 1. lib_symbols に追加（Transformer_1P_1S の直後、Transformer_1P_SS の前）
insert_marker = '\t\t\t(symbol "Device:Transformer_1P_SS"'
if "Device:Transformer_1P_2S" in sch:
    print("Transformer_1P_2S は既に lib_symbols にあります")
else:
    sch = sch.replace(insert_marker, sym_indented + "\n" + insert_marker, 1)
    print("lib_symbols に Transformer_1P_2S を追加しました")

# 2. L11 の lib_id を変更
# L11 インスタンスの特定: uuid "412443bb-..." を含む箇所
l11_block_marker = '(uuid "412443bb-e199-46c7-ad9e-ed2fcfd971bf")'
if l11_block_marker not in sch:
    print("ERROR: L11 の UUID が見つかりません")
    exit(1)

# lib_id 変更: L11 の symbol ブロック内だけを対象にするため前後コンテキストで置換
old_lib = '(lib_id "Device:Transformer_1P_1S")\n\t\t(at 345.44 307.34 0)'
new_lib = '(lib_id "Device:Transformer_1P_2S")\n\t\t(at 345.44 307.34 0)'
if old_lib in sch:
    sch = sch.replace(old_lib, new_lib, 1)
    print("L11 の lib_id を Transformer_1P_2S に変更しました")
else:
    print("ERROR: L11 の lib_id 置換対象が見つかりません")
    exit(1)

# 3. L11 インスタンスに pin 5, pin 6 を追加（pin "3" の直後、instances の前）
old_pins = (
    '\t\t\t(pin "3"\n\t\t\t\t(uuid "2852bddd-fe3a-4062-8d20-d4abd300fddc")\n\t\t\t)\n'
    '\t\t\t(instances'
)
new_pins = (
    '\t\t\t(pin "3"\n\t\t\t\t(uuid "2852bddd-fe3a-4062-8d20-d4abd300fddc")\n\t\t\t)\n'
    f'\t\t\t(pin "5"\n\t\t\t\t(uuid "{uuid.uuid4()}")\n\t\t\t)\n'
    f'\t\t\t(pin "6"\n\t\t\t\t(uuid "{uuid.uuid4()}")\n\t\t\t)\n'
    '\t\t\t(instances'
)
if old_pins in sch:
    sch = sch.replace(old_pins, new_pins, 1)
    print("L11 に pin 5, 6 を追加しました")
else:
    print("ERROR: L11 の pin 3 が見つかりません")
    idx = sch.index(l11_block_marker)
    print(sch[idx-600:idx+50])

# --- 書き出し ---
with open(SCH, "w", encoding="utf-8") as f:
    f.write(sch)
print("完了: PSN_TRX.kicad_sch を更新しました")
