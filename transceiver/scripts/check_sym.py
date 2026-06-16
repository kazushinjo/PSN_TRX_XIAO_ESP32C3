import re
sch = open(r"C:\Users\kazus\KiCad\PSN_TRX_New\PSN_TRX.kicad_sch", "r", encoding="utf-8").read()
lib_sym_start = sch.find("(lib_symbols")
lib_sym_end = sch.find("\n\t)\n\t(", lib_sym_start)
print(f"lib_symbols: {lib_sym_start} - {lib_sym_end}")
for m in re.finditer(r'"Device:Transformer_1P_2S"', sch):
    in_lib = lib_sym_start < m.start() < lib_sym_end
    context = sch[m.start()-30:m.start()+40]
    print(f"  pos={m.start()} in_lib={in_lib} ctx={repr(context)}")
