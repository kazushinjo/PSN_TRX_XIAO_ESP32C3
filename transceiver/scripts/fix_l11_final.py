"""
L11 シンボル最終修正スクリプト
- PSN_TRX:L_7T50_CT シンボルを lib_symbols に追加
- L11 の lib_id を PSN_TRX:L_7T50_CT に変更
- L11 インスタンスのピンを 1,2,3,4,5 に整理
"""
import uuid, re

SCH = r"C:\Users\kazus\KiCad\PSN_TRX_New\PSN_TRX.kicad_sch"

# ---- カスタムシンボル定義 ----------------------------------------
# ピン配置: 右(secondary+CT): SA(1)y=+5.08, CT(2)y=0, SB(3)y=-5.08
#           左(primary):      AA(4)y=+5.08, AB(5)y=-5.08
# 描画要素は Transformer_1P_1S のアーク群をそのまま流用

CUSTOM_SYM = r"""		(symbol "PSN_TRX:L_7T50_CT"
			(pin_names
				(offset 1.016)
				(hide yes)
			)
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "T"
				(at 0 7.62 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "L_7T50_CT"
				(at 0 -7.62 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" "PSN_TRX:L_FCZ07S_CT"
				(at 0 0 0)
				(hide yes)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Datasheet" ""
				(at 0 0 0)
				(hide yes)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Description" "Sato Denki FCZ 07S centre-tap transformer"
				(at 0 0 0)
				(hide yes)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(symbol "L_7T50_CT_0_1"
				(arc
					(start -1.27 3.81)
					(mid -1.656 2.9336)
					(end -2.54 2.5654)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -1.27 1.27)
					(mid -1.656 0.3936)
					(end -2.54 0.0254)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -1.27 -1.27)
					(mid -1.656 -2.1464)
					(end -2.54 -2.5146)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -1.27 -3.81)
					(mid -1.656 -4.6864)
					(end -2.54 -5.0546)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -2.54 5.08)
					(mid -1.642 4.708)
					(end -1.27 3.81)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -2.54 2.54)
					(mid -1.642 2.168)
					(end -1.27 1.27)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -2.54 0)
					(mid -1.642 -0.372)
					(end -1.27 -1.27)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start -2.54 -2.54)
					(mid -1.642 -2.912)
					(end -1.27 -3.81)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(polyline
					(pts (xy -0.635 5.08) (xy -0.635 -5.08))
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(polyline
					(pts (xy 0.635 -5.08) (xy 0.635 5.08))
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 1.2954 3.81)
					(mid 1.6457 4.7117)
					(end 2.54 5.08)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 1.2954 1.27)
					(mid 1.6457 2.1717)
					(end 2.54 2.54)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 1.2954 -1.27)
					(mid 1.6457 -0.3683)
					(end 2.54 0)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 2.54 2.5654)
					(mid 1.6599 2.9299)
					(end 1.2954 3.81)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 2.54 0.0254)
					(mid 1.6599 0.3899)
					(end 1.2954 1.27)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 2.54 -2.5146)
					(mid 1.6599 -2.1501)
					(end 1.2954 -1.27)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 1.3208 -3.81)
					(mid 1.6711 -2.9085)
					(end 2.5654 -2.54)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(arc
					(start 2.5654 -5.0546)
					(mid 1.6851 -4.6902)
					(end 1.3208 -3.81)
					(stroke (width 0) (type default))
					(fill (type none))
				)
				(polyline
					(pts (xy 2.54 0) (xy 3.81 0))
					(stroke (width 0) (type default))
					(fill (type none))
				)
			)
			(symbol "L_7T50_CT_1_1"
				(pin passive line
					(at 10.16 5.08 180)
					(length 7.62)
					(name "SA"
						(effects (font (size 1.27 1.27)))
					)
					(number "1"
						(effects (font (size 1.27 1.27)))
					)
				)
				(pin passive line
					(at 10.16 0 180)
					(length 7.62)
					(name "CT"
						(effects (font (size 1.27 1.27)))
					)
					(number "2"
						(effects (font (size 1.27 1.27)))
					)
				)
				(pin passive line
					(at 10.16 -5.08 180)
					(length 7.62)
					(name "SB"
						(effects (font (size 1.27 1.27)))
					)
					(number "3"
						(effects (font (size 1.27 1.27)))
					)
				)
				(pin passive line
					(at -10.16 5.08 0)
					(length 7.62)
					(name "AA"
						(effects (font (size 1.27 1.27)))
					)
					(number "4"
						(effects (font (size 1.27 1.27)))
					)
				)
				(pin passive line
					(at -10.16 -5.08 0)
					(length 7.62)
					(name "AB"
						(effects (font (size 1.27 1.27)))
					)
					(number "5"
						(effects (font (size 1.27 1.27)))
					)
				)
			)
			(embedded_fonts no)
		)
"""

with open(SCH, "r", encoding="utf-8") as f:
    sch = f.read()

lib_sym_start = sch.find("(lib_symbols")
lib_sym_end = sch.find("\n\t)\n\t(", lib_sym_start)

# 1. lib_symbols への挿入（末尾の \t\t)\n\t) の直前）
if "PSN_TRX:L_7T50_CT" in sch[lib_sym_start:lib_sym_end]:
    print("L_7T50_CT は既に lib_symbols にあります")
else:
    # lib_symbols の末尾: "...(embedded_fonts no)\n\t\t)\n\t)"
    close_marker = "\n\t\t)\n\t)\n"
    insert_pos = sch.rfind(close_marker, lib_sym_start, lib_sym_end + 10)
    if insert_pos == -1:
        print("ERROR: lib_symbols の末尾マーカーが見つかりません")
        exit(1)
    sch = sch[:insert_pos + len("\n\t\t)\n")] + CUSTOM_SYM + "\t)\n" + sch[insert_pos + len(close_marker):]
    print("lib_symbols に PSN_TRX:L_7T50_CT を追加しました")

# 2. L11 の lib_id を PSN_TRX:L_7T50_CT に変更
old_libid = '(lib_id "Device:Transformer_1P_2S")\n\t\t(at 345.44 307.34 0)'
new_libid = '(lib_id "PSN_TRX:L_7T50_CT")\n\t\t(at 345.44 307.34 0)'
if old_libid in sch:
    sch = sch.replace(old_libid, new_libid, 1)
    print("L11 の lib_id を PSN_TRX:L_7T50_CT に変更しました")
elif '(lib_id "PSN_TRX:L_7T50_CT")' in sch:
    print("L11 の lib_id は既に PSN_TRX:L_7T50_CT です")
else:
    print("ERROR: L11 の lib_id 置換対象が見つかりません")
    exit(1)

# 3. L11 ピンを 1,2,3,4,5 に整理（不要な pin "6" を削除）
old_pin6 = '\t\t(pin "6"\n\t\t\t(uuid "71a893a4-15e3-4b55-8675-ce3bcfd2f717")\n\t\t)\n'
if old_pin6 in sch:
    sch = sch.replace(old_pin6, "", 1)
    print("L11 の pin 6 を削除しました")
else:
    print("pin 6 は既に存在しません（スキップ）")

# ピン番号確認
l11_uuid = '412443bb-e199-46c7-ad9e-ed2fcfd971bf'
idx = sch.index(l11_uuid)
chunk = sch[idx:idx+600]
pins_found = re.findall(r'\(pin "(\d+)"', chunk)
print(f"L11 現在のピン: {pins_found}")

with open(SCH, "w", encoding="utf-8") as f:
    f.write(sch)
print("完了: PSN_TRX.kicad_sch を更新しました")
