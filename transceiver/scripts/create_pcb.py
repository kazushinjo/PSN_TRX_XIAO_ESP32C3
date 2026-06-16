#!/usr/bin/env python3
"""
Create PSN_TRX.kicad_pcb with 4-layer stackup (JLCPCB JLC7628).

Layer assignment:
  F.Cu   (L1): Signal / Components
  In1.Cu (L2): GND plane  (solid pour)
  In2.Cu (L3): Power plane (+9V / +5V zones)
  B.Cu   (L4): Signal / additional routing

Board: 100 x 150 mm, 4x M3 mounting holes (3.5 mm from each corner)
"""

import uuid
from pathlib import Path

OUT = Path('PSN_TRX.kicad_pcb')

W, H = 150.0, 100.0   # board width × height [mm]
CORNER = 3.5          # mounting hole offset from edge [mm]


def uid():
    return str(uuid.uuid4())


def mounting_hole(ref: str, x: float, y: float) -> str:
    """MountingHole_3.2mm_M3 footprint block."""
    fp_uid   = uid()
    pad_uid  = uid()
    return f'''\t(footprint "MountingHole:MountingHole_3.2mm_M3"
\t\t(layer "F.Cu")
\t\t(uuid "{fp_uid}")
\t\t(at {x} {y})
\t\t(descr "Mounting Hole 3.2mm, no annular, M3")
\t\t(tags "mounting hole 3.2mm no annular m3")
\t\t(attr exclude_from_pos_files exclude_from_bom)
\t\t(fp_text reference "{ref}"
\t\t\t(at 0 -4.2)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(fp_text value "MountingHole_3.2mm_M3"
\t\t\t(at 0 4.2)
\t\t\t(layer "F.Fab")
\t\t\t(uuid "{uid()}")
\t\t\t(effects (font (size 1 1) (thickness 0.15)))
\t\t)
\t\t(fp_circle
\t\t\t(center 0 0) (end 3.2 0)
\t\t\t(stroke (width 0.15) (type solid))
\t\t\t(fill none)
\t\t\t(layer "F.SilkS")
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(fp_circle
\t\t\t(center 0 0) (end 3.5 0)
\t\t\t(stroke (width 0.05) (type solid))
\t\t\t(fill none)
\t\t\t(layer "F.CrtYd")
\t\t\t(uuid "{uid()}")
\t\t)
\t\t(pad "" np_thru_hole circle
\t\t\t(at 0 0)
\t\t\t(size 3.2 3.2)
\t\t\t(drill 3.2)
\t\t\t(layers "*.Cu" "*.Mask")
\t\t\t(uuid "{pad_uid}")
\t\t)
\t)'''


PCB_TEMPLATE = f'''\
(kicad_pcb
\t(version 20241209)
\t(generator "pcbnew")
\t(generator_version "9.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(1 "In1.Cu" power "GND Plane")
\t\t(2 "In2.Cu" power "Power Plane (+9V/+5V)")
\t\t(31 "B.Cu" signal)
\t\t(32 "B.Adhes" user "B.Adhesive")
\t\t(33 "F.Adhes" user "F.Adhesive")
\t\t(34 "B.Paste" user)
\t\t(35 "F.Paste" user)
\t\t(36 "B.SilkS" user "B.Silkscreen")
\t\t(37 "F.SilkS" user "F.Silkscreen")
\t\t(38 "B.Mask" user)
\t\t(39 "F.Mask" user)
\t\t(40 "Dwgs.User" user "User.Drawings")
\t\t(41 "Cmts.User" user "User.Comments")
\t\t(44 "Edge.Cuts" user)
\t\t(45 "Margin" user)
\t\t(46 "B.CrtYd" user "B.Courtyard")
\t\t(47 "F.CrtYd" user "F.Courtyard")
\t\t(48 "B.Fab" user "B.Fabrication")
\t\t(49 "F.Fab" user "F.Fabrication")
\t)
\t(setup
\t\t(pad_to_mask_clearance 0.05)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask"  (type "Top Solder Mask") (thickness 0.01))
\t\t\t(layer "F.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "dielectric 1"
\t\t\t\t(type "prepreg")
\t\t\t\t(thickness 0.21)
\t\t\t\t(material "2116")
\t\t\t\t(epsilon_r 4.6)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "In1.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.0175)
\t\t\t)
\t\t\t(layer "dielectric 2"
\t\t\t\t(type "core")
\t\t\t\t(thickness 1.065)
\t\t\t\t(material "FR4")
\t\t\t\t(epsilon_r 4.5)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "In2.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.0175)
\t\t\t)
\t\t\t(layer "dielectric 3"
\t\t\t\t(type "prepreg")
\t\t\t\t(thickness 0.21)
\t\t\t\t(material "2116")
\t\t\t\t(epsilon_r 4.6)
\t\t\t\t(loss_tangent 0.02)
\t\t\t)
\t\t\t(layer "B.Cu"
\t\t\t\t(type "copper")
\t\t\t\t(thickness 0.035)
\t\t\t)
\t\t\t(layer "B.Mask"  (type "Bottom Solder Mask") (thickness 0.01))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))
\t\t\t(copper_finish "HASL(with lead)")
\t\t\t(dielectric_constraints no)
\t\t\t(board_thickness 1.6)
\t\t)
\t\t(pcbplotparams
\t\t\t(outputformat 1)
\t\t\t(usegerberextensions no)
\t\t\t(usegerberattributes yes)
\t\t\t(usegerberadvancedattributes yes)
\t\t\t(creategerberjobfile yes)
\t\t\t(outputdirectory "gerber/")
\t\t)
\t)
\t(net 0 "")
\t(net 1 "GND")
\t(net 2 "+9V")
\t(net 3 "+5V")
\t(net_class "Default" ""
\t\t(clearance 0.2)
\t\t(trace_width 0.25)
\t\t(via_diameter 0.8)
\t\t(via_drill 0.4)
\t\t(microvia_diameter 0.3)
\t\t(microvia_drill 0.1)
\t\t(diff_pair_width 0.2)
\t\t(diff_pair_gap 0.25)
\t)
\t(net_class "Power" "Power supply traces"
\t\t(clearance 0.3)
\t\t(trace_width 0.8)
\t\t(via_diameter 1.2)
\t\t(via_drill 0.6)
\t\t(microvia_diameter 0.3)
\t\t(microvia_drill 0.1)
\t\t(diff_pair_width 0.8)
\t\t(diff_pair_gap 0.3)
\t\t(add_net "+9V")
\t\t(add_net "+5V")
\t)
\t(net_class "RF" "50MHz RF signal paths"
\t\t(clearance 0.3)
\t\t(trace_width 0.3)
\t\t(via_diameter 0.8)
\t\t(via_drill 0.4)
\t\t(microvia_diameter 0.3)
\t\t(microvia_drill 0.1)
\t\t(diff_pair_width 0.3)
\t\t(diff_pair_gap 0.3)
\t)
\t(board_rule_constraints
\t\t(min_copper_edge_clearance 0.3)
\t\t(min_hole_to_hole 0.25)
\t\t(min_silk_clearance 0.1)
\t\t(use_height_for_length_calcs no)
\t)
{mounting_hole("H1", CORNER,     CORNER)}
{mounting_hole("H2", W - CORNER, CORNER)}
{mounting_hole("H3", CORNER,     H - CORNER)}
{mounting_hole("H4", W - CORNER, H - CORNER)}
\t(gr_rect
\t\t(start 0 0)
\t\t(end {W} {H})
\t\t(stroke (width 0.05) (type solid))
\t\t(layer "Edge.Cuts")
\t\t(uuid "{uid()}")
\t)
\t(gr_text "F.Cu  = Signal / Components\\nIn1.Cu = GND Plane (solid)\\nIn2.Cu = Power Plane (+9V/+5V)\\nB.Cu  = Signal / Routing"
\t\t(at 2 {H + 5})
\t\t(layer "Cmts.User")
\t\t(uuid "{uid()}")
\t\t(effects (font (size 1.5 1.5) (thickness 0.15)))
\t)
)
'''


def main():
    if OUT.exists():
        print(f'{OUT} already exists. Delete it first if you want to regenerate.')
        return
    OUT.write_text(PCB_TEMPLATE, encoding='utf-8')
    print(f'Created: {OUT}')
    print(f'  Board size  : {W} x {H} mm')
    print(f'  Layers      : 4 (F.Cu / In1.Cu GND / In2.Cu Power / B.Cu)')
    print(f'  Stackup     : JLCPCB JLC7628, total 1.6 mm')
    print(f'  Mounting holes: H1-H4, M3 (φ3.2mm), offset {CORNER}mm from corners')
    print()
    print('Next step: Open KiCad PCBnew, then')
    print('  Tools > Update PCB from Schematic  (Ctrl+Shift+U)')
    print('  to import all components from the schematic.')


if __name__ == '__main__':
    main()
