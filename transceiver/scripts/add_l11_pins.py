import uuid

SCH = r"C:\Users\kazus\KiCad\PSN_TRX_New\PSN_TRX.kicad_sch"
with open(SCH, "r", encoding="utf-8") as f:
    sch = f.read()

old_pins = '\t\t(pin "3"\n\t\t\t(uuid "2852bddd-fe3a-4062-8d20-d4abd300fddc")\n\t\t)\n\t\t(instances'
pin5_uuid = str(uuid.uuid4())
pin6_uuid = str(uuid.uuid4())
new_pins = (
    '\t\t(pin "3"\n\t\t\t(uuid "2852bddd-fe3a-4062-8d20-d4abd300fddc")\n\t\t)\n'
    + '\t\t(pin "5"\n\t\t\t(uuid "' + pin5_uuid + '")\n\t\t)\n'
    + '\t\t(pin "6"\n\t\t\t(uuid "' + pin6_uuid + '")\n\t\t)\n'
    + '\t\t(instances'
)

if old_pins in sch:
    sch = sch.replace(old_pins, new_pins, 1)
    print("L11 に pin 5, 6 を追加しました")
    with open(SCH, "w", encoding="utf-8") as f:
        f.write(sch)
    print("ファイルを保存しました")
else:
    print("ERROR: パターンが見つかりません")
