#!/usr/bin/env python3
"""Add 4x M3 mounting hole symbols (H1-H4) to PSN_TRX.kicad_sch."""

import re
import shutil
import uuid
from pathlib import Path

SCH = Path('PSN_TRX.kicad_sch')
ROOT_UUID = '50835569-93ad-4c8c-aafc-424a6a3761ef'
FP = 'MountingHole:MountingHole_3.2mm_M3'

# ── lib_symbols entry for Mechanical:MountingHole ────────────────────────────
LIB_ENTRY = '''		(symbol "Mechanical:MountingHole"
			(pin_names
				(offset 1.016)
			)
			(exclude_from_sim no)
			(in_bom no)
			(on_board yes)
			(in_pos_files yes)
			(duplicate_pin_numbers_are_jumpers no)
			(property "Reference" "H"
				(at 0 5.08 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Value" "MountingHole"
				(at 0 3.175 0)
				(show_name no)
				(do_not_autoplace no)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Footprint" ""
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Datasheet" "~"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(property "Description" "Mounting Hole without connection"
				(at 0 0 0)
				(show_name no)
				(do_not_autoplace no)
				(hide yes)
				(effects
					(font
						(size 1.27 1.27)
					)
				)
			)
			(symbol "MountingHole_0_1"
				(fp_circle
					(center 0 0)
					(end 1.6 0)
					(stroke
						(width 0.1)
						(type default)
					)
					(fill
						(type none)
					)
				)
			)
		)'''


def make_hole_symbol(ref: str, x: float, y: float) -> str:
    """Generate a MountingHole symbol instance."""
    sym_uuid  = str(uuid.uuid4())
    pin1_uuid = str(uuid.uuid4())
    return f'''
\t(symbol
\t\t(lib_id "Mechanical:MountingHole")
\t\t(at {x} {y} 0)
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom no)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(uuid "{sym_uuid}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {x} {y - 3.81} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "MountingHole"
\t\t\t(at {x} {y - 5.715} 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" "{FP}"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" "~"
\t\t\t(at {x} {y} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(instances
\t\t\t(project "PSN_TRX"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)'''


def main():
    bak = SCH.with_suffix('.kicad_sch.bak3')
    shutil.copy(SCH, bak)

    content = SCH.read_text(encoding='utf-8')

    # Skip if already added
    if '"H1"' in content:
        print('Mounting holes already present.')
        return

    # 1. Add lib_symbols entry if not present
    if '"Mechanical:MountingHole"' not in content:
        # Insert before closing ) of lib_symbols
        content = content.replace(
            '\n\t)\n\t(junction',  # end of lib_symbols
            '\n' + LIB_ENTRY + '\n\t)\n\t(junction',
            1,
        )
        print('Added Mechanical:MountingHole to lib_symbols.')

    # 2. Add H1-H4 instances (placed in top-right area of schematic, spread out)
    holes = [
        ('H1', 760, 30),   # top-left corner label
        ('H2', 780, 30),   # top-right corner label
        ('H3', 760, 50),   # bottom-left corner label
        ('H4', 780, 50),   # bottom-right corner label
    ]

    blocks = ''.join(make_hole_symbol(ref, x, y) for ref, x, y in holes)

    insert_pos = content.rfind('\n)')
    content = content[:insert_pos] + blocks + content[insert_pos:]

    SCH.write_text(content, encoding='utf-8')
    print('Added H1, H2, H3, H4 (M3 mounting holes) to schematic.')
    print(f'Footprint: {FP}')
    print('\nPCB placement (corner offset 3.5mm from edge):')
    print('  H1: top-left     H2: top-right')
    print('  H3: bottom-left  H4: bottom-right')


if __name__ == '__main__':
    main()
