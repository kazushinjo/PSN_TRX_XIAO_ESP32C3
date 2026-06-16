#!/usr/bin/env python3
"""
Fix component overlap by applying repulsive spacing.
Each component pushes nearby components away.
"""

import sys, math
from pathlib import Path

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
mm = pcbnew.FromMM
to_mm = pcbnew.ToMM

# Minimum clearance per DRC rule
MIN_CLEARANCE = 0.25  # mm

def get_component_size(fp):
    """Estimate component footprint size."""
    bbox = fp.GetBoundingBox()
    w = to_mm(bbox.GetWidth())
    h = to_mm(bbox.GetHeight())
    return max(w, h) / 2  # radius estimate

def main():
    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    X_MIN, X_MAX = 5, 145
    Y_MIN, Y_MAX = 5, 95

    components = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        pos = fp.GetPosition()
        x, y = to_mm(pos.x), to_mm(pos.y)
        size = get_component_size(fp)
        components.append({
            'ref': ref,
            'fp': fp,
            'x': x,
            'y': y,
            'size': size,
            'vx': 0,
            'vy': 0,
        })

    print(f'Loaded {len(components)} components')
    print(f'Applying repulsive spacing...')

    # Iterative relaxation: push overlapping components apart
    for iteration in range(5):
        max_move = 0
        for i, comp_i in enumerate(components):
            fx, fy = 0, 0
            for j, comp_j in enumerate(components):
                if i == j:
                    continue
                dx = comp_i['x'] - comp_j['x']
                dy = comp_i['y'] - comp_j['y']
                dist = math.sqrt(dx**2 + dy**2)

                min_dist = comp_i['size'] + comp_j['size'] + MIN_CLEARANCE
                if dist < min_dist and dist > 0.01:
                    # Repulsive force
                    force = (min_dist - dist) / dist
                    fx += dx * force * 0.1
                    fy += dy * force * 0.1

            # Limit movement and apply
            move = math.sqrt(fx**2 + fy**2)
            if move > max_move:
                max_move = move

            # Clamp movement
            if move > 2:
                scale = 2 / move
                fx *= scale
                fy *= scale

            comp_i['x'] += fx
            comp_i['y'] += fy

            # Bounds checking
            comp_i['x'] = max(X_MIN + 2, min(X_MAX - 2, comp_i['x']))
            comp_i['y'] = max(Y_MIN + 2, min(Y_MAX - 2, comp_i['y']))

        print(f'  Iteration {iteration + 1}: max_move={max_move:.3f}mm')
        if max_move < 0.05:
            break

    # Apply positions back to PCB
    for comp in components:
        comp['fp'].SetPosition(pcbnew.VECTOR2I(mm(comp['x']), mm(comp['y'])))

    board.Save(str(PCB_FILE))
    print(f'\nFixed spacing. Running DRC...')

    # Run DRC to verify
    import subprocess
    result = subprocess.run([
        '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli', 'pcb', 'drc',
        '--output', 'PSN_TRX_drc_fixed.rpt',
        str(PCB_FILE)
    ], capture_output=True, text=True)

    # Parse result
    output = result.stdout + result.stderr
    if '0 個の違反' in output or 'No DRC violations' in output:
        print('✓ DRC PASSED - no violations')
    else:
        # Count violations
        import re
        match = re.search(r'(\d+) 個の違反', output)
        if match:
            count = match.group(1)
            print(f'⚠ DRC: {count} violations remain (reduced from 848)')
        else:
            print('DRC report generated: PSN_TRX_drc_fixed.rpt')


if __name__ == '__main__':
    main()
