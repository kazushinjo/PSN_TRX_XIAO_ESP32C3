#!/usr/bin/env python3
"""
KiCad スケマティックから部品表（BOM）を生成するスクリプト。
Reference と Value でグループ化し、CSV と Markdown 形式で出力。
"""

import re
import csv
from collections import defaultdict
from pathlib import Path


def parse_s_expression(text, depth=0):
    """簡易 S 式パーサー。"""
    result = []
    i = 0
    while i < len(text):
        if text[i] == '(':
            # ブロックの開始
            close = find_matching_paren(text, i)
            inner = text[i+1:close]
            result.append(parse_s_expression(inner, depth+1))
            i = close + 1
        elif text[i] == ')':
            break
        elif text[i] in ' \t\n':
            i += 1
        else:
            # トークン
            j = i
            while j < len(text) and text[j] not in '() \t\n':
                if text[j] == '"':
                    # 文字列
                    j += 1
                    while j < len(text) and text[j] != '"':
                        j += 1
                    j += 1
                else:
                    j += 1
            token = text[i:j].strip()
            if token:
                result.append(token)
            i = j
    return result


def find_matching_paren(text, start):
    """対応する閉じ括弧を見つける。"""
    depth = 1
    for i in range(start + 1, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def extract_property(block_text, prop_name):
    """ブロックテキストからプロパティ値を抽出。"""
    pattern = f'\\(property\\s+"{ re.escape(prop_name)}"\\s+"([^"]+)"'
    match = re.search(pattern, block_text)
    return match.group(1) if match else ""


def parse_kicad_sch(filepath):
    """KiCad スケマティック (.kicad_sch) をパースして部品情報を抽出。"""
    components = []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # (symbol (lib_id ...) (at ...) ... (property "Reference" ...) (property "Value" ...) ...) パターン
    # シンボルインスタンス（sheet内）を見つける
    symbol_pattern = r'\(symbol\s+\(lib_id\s+"[^"]+"\)'

    for match in re.finditer(symbol_pattern, content):
        start = match.start()
        # 対応する閉じ括弧を探す
        depth = 1
        i = match.end()
        while i < len(content) and depth > 0:
            if content[i] == '(':
                depth += 1
            elif content[i] == ')':
                depth -= 1
            i += 1

        if depth == 0:
            block = content[start:i]

            ref = extract_property(block, "Reference")
            value = extract_property(block, "Value")
            footprint = extract_property(block, "Footprint")

            # パワーシンボルは除外
            if ref and not ref.startswith('#'):
                components.append({
                    'Reference': ref,
                    'Value': value,
                    'Footprint': footprint
                })

    return components


def group_bom(components):
    """部品を Value + Footprint でグループ化。"""
    groups = defaultdict(list)

    for comp in components:
        key = (comp['Value'], comp['Footprint'])
        groups[key].append(comp['Reference'])

    return groups


def sort_references(refs_str):
    """参照をソート（数値考慮）。"""
    refs = refs_str.split(', ')
    def ref_key(ref):
        match = re.match(r'([A-Z]+)(\d+)', ref)
        if match:
            return (match.group(1), int(match.group(2)))
        return (ref, 0)
    return ', '.join(sorted(refs, key=ref_key))


def generate_csv(groups, output_file):
    """BOMをCSV形式で出力。"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Reference', 'Value', 'Footprint', 'Qty'])

        for (value, footprint), refs in sorted(groups.items()):
            refs_sorted = sorted(refs, key=lambda x: (x[0], int(re.search(r'\\d+', x).group()) if re.search(r'\\d+', x) else 0))
            refs_str = ', '.join(refs_sorted)
            writer.writerow([refs_str, value, footprint, len(refs)])


def generate_markdown(groups, output_file):
    """BOMをMarkdown形式で出力（カテゴリ別）。"""

    # カテゴリ分類（Reference の最初の文字）
    categories = defaultdict(list)

    for (value, footprint), refs in groups.items():
        cat = refs[0][0]  # 最初のリファレンスの最初の文字
        refs_sorted = sorted(refs, key=lambda x: (x[0], int(re.search(r'\\d+', x).group()) if re.search(r'\\d+', x) else 0))
        categories[cat].append({
            'references': ', '.join(refs_sorted),
            'value': value,
            'footprint': footprint,
            'qty': len(refs)
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('# PSN_TRX 部品表（BOM）\n\n')
        f.write('50MHz 帯 PSN 方式 SSB トランシーバ。\n')
        f.write('スケマティック (`PSN_TRX.kicad_sch`) から自動生成。\n\n')
        f.write('機械可読版は [`bom.csv`](bom.csv)。\n\n---\n\n')

        # カテゴリごとに表を生成
        cat_order = ['R', 'C', 'L', 'D', 'T', 'TC', 'VR', 'Q', 'IC', 'LED', 'X', 'SW', 'MIC']
        cat_names = {
            'R': '抵抗 R',
            'C': 'コンデンサ C',
            'L': 'コイル L',
            'D': 'ダイオード D',
            'T': 'トランス T',
            'Q': 'トランジスタ Q',
            'IC': 'IC',
            'LED': 'LED',
            'X': '水晶振動子',
            'SW': 'スイッチ',
            'VR': '可変抵抗',
            'TC': 'トリマコンデンサ',
            'MIC': 'マイク'
        }

        for cat in cat_order:
            if cat not in categories:
                continue
            cat_name = cat_names.get(cat, cat)
            f.write(f'## {cat_name}\n\n')
            f.write('| Reference | Value | Footprint | Qty |\n')
            f.write('|---|---|---|---|\n')

            for item in sorted(categories[cat], key=lambda x: x['references']):
                fp = item['footprint'] if item['footprint'] else '未割当'
                f.write(f"| {item['references']} | {item['value']} | {fp} | {item['qty']} |\n")

            f.write('\n')


if __name__ == '__main__':
    sch_file = Path('PSN_TRX.kicad_sch')

    print(f"Parsing {sch_file}...")
    components = parse_kicad_sch(sch_file)
    print(f"Found {len(components)} components.")

    if not components:
        print("Error: No components found!")
        exit(1)

    print("Grouping by Value and Footprint...")
    groups = group_bom(components)

    print("Generating CSV...")
    generate_csv(groups, 'bom.csv')

    print("Generating Markdown...")
    generate_markdown(groups, 'BOM.md')

    print("Done!")
    print(f"CSV: bom.csv ({len(groups)} unique values)")
    print(f"Markdown: BOM.md")
