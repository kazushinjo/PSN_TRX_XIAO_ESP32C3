#!/usr/bin/env python3
"""
Update PCB: add K1 (G5V-2 relay) footprint and update placement.
Run with KiCad bundled Python.
"""

import sys, re
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM

FP_SEARCH = [
    PROJECT_DIR,
    Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'),
]

def find_fp(lib_ref):
    if ':' not in lib_ref:
        return None
    lib, name = lib_ref.split(':', 1)
    for base in FP_SEARCH:
        p = base / f'{lib}.pretty' / f'{name}.kicad_mod'
        if p.exists():
            return base / f'{lib}.pretty', name
    return None

def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    # Check if K1 already exists
    existing = {fp.GetReference() for fp in board.GetFootprints()}
    print(f'Existing footprints: {len(existing)}')

    changes = []

    # 1. Remove SW2/SW3 if they exist (they shouldn't, but clean up)
    for ref in ['SW2', 'SW3']:
        fp = board.FindFootprintByReference(ref)
        if fp:
            board.Remove(fp)
            changes.append(f'Removed: {ref}')

    # 2. Add K1 (G5V-2 DPDT relay) in BPF_ANT block (x=5~40, y=5~47)
    if 'K1' not in existing:
        loc = find_fp('Relay_THT:Relay_DPDT_Omron_G5V-2')
        if loc is None:
            # Try direct path
            fp_dir2 = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Relay_THT.pretty')
            loc = (fp_dir2, 'Relay_DPDT_Omron_G5V-2')
        if loc:
            fp_dir, fp_name = loc
            fp = pcbnew.FootprintLoad(str(fp_dir), fp_name)
            if fp:
                fp.SetReference('K1')
                fp.SetValue('G5V-2')
                # Place in BPF_ANT block, near SW1
                fp.SetPosition(pcbnew.VECTOR2I(mm(22), mm(38)))
                fp.SetOrientationDegrees(0)
                board.Add(fp)
                changes.append('Added: K1 (G5V-2) at (22, 38)mm in BPF_ANT block')
            else:
                print('ERROR: could not load G5V-2 footprint')
        else:
            print('ERROR: G5V-2 footprint file not found')
    else:
        # Update K1 position to BPF_ANT block if it's outside the board
        fp = board.FindFootprintByReference('K1')
        if fp:
            pos = fp.GetPosition()
            x_mm = pcbnew.ToMM(pos.x)
            if x_mm > 100:  # if in overflow area, move to BPF_ANT
                fp.SetPosition(pcbnew.VECTOR2I(mm(22), mm(38)))
                changes.append('Moved: K1 to (22, 38)mm in BPF_ANT block')

    board.Save(str(PCB_FILE))

    print('\nChanges:')
    for c in changes:
        print(f'  {c}')
    print(f'\nTotal footprints: {len(list(board.GetFootprints()))}')
    print(f'Saved: {PCB_FILE}')

if __name__ == '__main__':
    main()
