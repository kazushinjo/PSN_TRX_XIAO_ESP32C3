#!/usr/bin/env python3
"""
set_vertical_footprints.py
固定抵抗(Device:R)とダイオード(Device:D)の全インスタンスに、
縦実装(vertical)フットプリントを一括割り当てする。

  Device:R -> Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical  (1/4W)
  Device:D -> Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp           (1N60/DO-35)

Device:R_Potentiometer / Device:R_Variable / Device:LED は lib_id が一致しない
ため自動的に対象外。lib_symbols 定義はインスタンス検出(\t(symbol\\n)で除外。
"""

import re

SCH = r"C:\Users\shinjo\OneDrive\デスクトップ\KiCad\PSN_TRX\PSN_TRX.kicad_sch"

R_FP = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical"
D_FP = "Diode_THT:D_DO-35_SOD27_P2.54mm_Vertical_CathodeUp"

MARKER = "\t(symbol\n"   # トップレベルのシンボルインスタンス


def balanced_end(s, start):
    depth = 0
    i = start
    while i < len(s):
        c = s[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise RuntimeError("括弧が閉じていません")


def main():
    t = open(SCH, encoding="utf-8").read()
    parts = []
    idx = 0
    n_r = n_d = 0
    while True:
        m = t.find(MARKER, idx)
        if m == -1:
            parts.append(t[idx:])
            break
        paren = t.index("(", m)          # MARKER 内の '(' 位置
        end = balanced_end(t, paren)
        block = t[paren:end]

        fp = None
        if '(lib_id "Device:R")' in block:
            fp = R_FP
        elif '(lib_id "Device:D")' in block:
            fp = D_FP

        if fp is not None:
            mm = re.search(r'\(property "Footprint" "[^"]*"', block)
            if not mm:
                raise RuntimeError("Footprint プロパティが見つかりません")
            block = block[:mm.start()] + '(property "Footprint" "%s"' % fp + block[mm.end():]
            if fp == R_FP:
                n_r += 1
            else:
                n_d += 1

        parts.append(t[idx:paren])       # 直前テキスト + '\t'
        parts.append(block)
        idx = end

    t2 = "".join(parts)
    if t2.count("(") != t2.count(")"):
        raise RuntimeError("括弧不一致 ( %d vs ) %d" % (t2.count("("), t2.count(")")))

    open(SCH, "w", encoding="utf-8").write(t2)
    print("Device:R に縦実装FP割当: %d 個" % n_r)
    print("Device:D に縦実装FP割当: %d 個" % n_d)
    print("括弧バランス OK (%d)" % t2.count("("))
    print("書き出し完了:", SCH)


if __name__ == "__main__":
    main()
