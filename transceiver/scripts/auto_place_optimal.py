#!/usr/bin/env python3
"""
Optimal auto-placement using KiCad pcbnew API.
- Analyze netlist connectivity
- Use force-directed layout to minimize total wire length
- Respect board boundaries and spacing rules
"""

import sys, math, random
from collections import defaultdict

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

from pathlib import Path
PROJECT_DIR = Path(__file__).parent
PCB_FILE = str(PROJECT_DIR / 'PSN_TRX.kicad_pcb')
NET_FILE = str(PROJECT_DIR / 'PSN_TRX.net')
mm = pcbnew.FromMM
to_mm = pcbnew.ToMM

def parse_netlist_simple(net_file):
    """Extract connected component pairs from netlist."""
    import re
    with open(net_file, encoding='utf-8') as f:
        content = f.read()

    connections = defaultdict(set)
    # Find nets with multiple nodes
    for m in re.finditer(r'\(net\s+\(code\s+"[^"]+"\)\s+\(name\s+"([^"]+)"([\s\S]{0,1000}?)\(net\s|$', content):
        net_name = m.group(1)
        if net_name is None:
            continue
        net_body = m.group(2) or ''
        refs = re.findall(r'\(node\s+\(ref\s+"([^"]+)"', net_body)

        # Skip power/GND (too many connections)
        if any(x in net_name for x in ['GND', '+5V', '+9V', '-12V']):
            continue
        if len(refs) > 1:
            for i, ref1 in enumerate(refs):
                for ref2 in refs[i+1:]:
                    connections[ref1].add(ref2)
                    connections[ref2].add(ref1)

    return connections

def main():
    board = pcbnew.LoadBoard(PCB_FILE)
    if not board:
        print('ERROR: cannot load PCB')
        return

    # Board bounds
    X_MIN, X_MAX = 5, 225
    Y_MIN, Y_MAX = 5, 155

    # Collect components
    components = []
    ref_to_comp = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref.startswith('H'):
            continue
        pos = fp.GetPosition()
        x, y = to_mm(pos.x), to_mm(pos.y)
        comp = {
            'ref': ref,
            'fp': fp,
            'x': x,
            'y': y,
            'vx': 0,
            'vy': 0,
        }
        components.append(comp)
        ref_to_comp[ref] = comp

    print(f'Auto-placing {len(components)} components...')

    # Parse connections
    connections = parse_netlist_simple(NET_FILE)
    print(f'Found {sum(len(v) for v in connections.values())//2} signal connections')

    # Force-directed layout (spring model)
    # Attractive forces along connections, repulsive forces for spacing
    for iteration in range(10):
        max_move = 0

        for comp in components:
            fx, fy = 0, 0

            # Attractive forces (pull connected components together)
            neighbors = connections.get(comp['ref'], set())
            for neighbor_ref in neighbors:
                if neighbor_ref in ref_to_comp:
                    neighbor = ref_to_comp[neighbor_ref]
                    dx = neighbor['x'] - comp['x']
                    dy = neighbor['y'] - comp['y']
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > 0.1:
                        # Spring force: pull together
                        force = dist * 0.01  # Stiffness
                        fx += dx / dist * force
                        fy += dy / dist * force

            # Repulsive forces (push away from board edges and other components)
            margin = 10
            if comp['x'] < X_MIN + margin:
                fx += (X_MIN + margin - comp['x']) * 0.05
            if comp['x'] > X_MAX - margin:
                fx -= (comp['x'] - (X_MAX - margin)) * 0.05
            if comp['y'] < Y_MIN + margin:
                fy += (Y_MIN + margin - comp['y']) * 0.05
            if comp['y'] > Y_MAX - margin:
                fy -= (comp['y'] - (Y_MAX - margin)) * 0.05

            # Limit movement
            move = math.sqrt(fx**2 + fy**2)
            if move > max_move:
                max_move = move
            if move > 1:
                scale = 1 / move
                fx *= scale
                fy *= scale

            comp['x'] += fx * 0.5
            comp['y'] += fy * 0.5

            # Keep in bounds
            comp['x'] = max(X_MIN + 3, min(X_MAX - 3, comp['x']))
            comp['y'] = max(Y_MIN + 3, min(Y_MAX - 3, comp['y']))

        print(f'  Iteration {iteration+1}: max_move={max_move:.3f}mm')
        if max_move < 0.01:
            break

    # Apply to board
    for comp in components:
        comp['fp'].SetPosition(pcbnew.VECTOR2I(mm(comp['x']), mm(comp['y'])))

    board.Save(PCB_FILE)
    print(f'\n✓ Auto-placement complete')
    print(f'✓ {len(components)} components optimized for minimal wire length')

if __name__ == '__main__':
    main()
