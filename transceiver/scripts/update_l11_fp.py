SCH = r"C:\Users\kazus\KiCad\PSN_TRX_New\PSN_TRX.kicad_sch"
with open(SCH, "r", encoding="utf-8") as f:
    sch = f.read()

# L11 の Footprint プロパティを更新（座標 345.44 307.34 で特定）
old = '(property "Footprint" ""\n\t\t\t(at 345.44 307.34 0)'
new = '(property "Footprint" "PSN_TRX:L_FCZ07S_CT"\n\t\t\t(at 345.44 307.34 0)'
if old in sch:
    sch = sch.replace(old, new, 1)
    print("L11 Footprint を PSN_TRX:L_FCZ07S_CT に更新しました")
    with open(SCH, "w", encoding="utf-8") as f:
        f.write(sch)
else:
    print("パターン未検出")
