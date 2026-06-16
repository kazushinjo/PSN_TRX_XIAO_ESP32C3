#!/usr/bin/env python3
"""
Place components following schematic topology:
- Analyze netlist to find connected component groups
- Place related TR/C/R together (not by function block)
- Arrange groups in signal flow order (left to right)
"""

import sys, re, math
from pathlib import Path
from collections import defaultdict, deque

sys.path.insert(0, '/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages')
import pcbnew

PROJECT_DIR = Path(__file__).parent
PCB_FILE    = PROJECT_DIR / 'PSN_TRX.kicad_pcb'
NET_FILE    = PROJECT_DIR / 'PSN_TRX.net'
mm = pcbnew.FromMM

# ────────────────────────────────────────────────────────────────────────────
# Parse netlist to build connection graph
# ────────────────────────────────────────────────────────────────────────────

def parse_netlist(net_file):
    """Parse netlist and return:
    - comp_nets: {ref: set of net names connected to this component}
    - net_comps: {net_name: set of component refs on this net}
    """
    with open(net_file, encoding='utf-8') as f:
        content = f.read()

    comp_nets = defaultdict(set)
    net_comps = defaultdict(set)

    # Simple regex: find each (net ...) block and extract nodes
    # Pattern: (net (code "...") (name "...") ... (node (ref "...") ...) ... )
    pattern = r'\(net\s+\(code\s+"[^"]+"\)\s+\(name\s+"([^"]+)"([\s\S]{0,2000}?)\(net\s|$'

    for m in re.finditer(pattern, content):
        net_name = m.group(1)
        net_body = m.group(2) if m.group(2) else ''

        # Find all (node (ref "...") ...)
        for node_m in re.finditer(r'\(node\s+\(ref\s+"([^"]+)"', net_body):
            ref = node_m.group(1)
            if not ref.startswith('H'):  # Skip mounting holes
                comp_nets[ref].add(net_name)
                net_comps[net_name].add(ref)

    return comp_nets, net_comps


def find_component_clusters(comp_nets, net_comps, max_cluster_size=20):
    """
    Find connected components using BFS on signal nets (exclude power/GND).
    Returns list of component sets.
    """
    # Exclude global power/ground nets (they connect too many components)
    global_nets = {'GND', '+5V', '+9V', '-12V', 'GND_ISO', 'VBUS'}
    signal_nets = {n for n in net_comps.keys()
                   if not any(g in n for g in global_nets)}

    visited = set()
    clusters = []

    def bfs(start_ref):
        cluster = set()
        queue = deque([start_ref])
        visited.add(start_ref)

        while queue and len(cluster) < max_cluster_size:
            ref = queue.popleft()
            cluster.add(ref)

            # Find all components connected via shared signal nets
            for net in comp_nets.get(ref, set()):
                if net in signal_nets:  # Only signal nets, not power
                    for other_ref in net_comps.get(net, set()):
                        if other_ref not in visited and other_ref not in cluster:
                            visited.add(other_ref)
                            queue.append(other_ref)

        return cluster

    # Start BFS from each unvisited component (except those already in a cluster)
    all_refs = sorted(comp_nets.keys())
    for ref in all_refs:
        if ref not in visited:
            cluster = bfs(ref)
            if cluster:
                clusters.append(cluster)

    return clusters


# ────────────────────────────────────────────────────────────────────────────
# Layout strategy: place clusters in signal flow order
# ────────────────────────────────────────────────────────────────────────────

SIGNAL_FLOW_ORDER = [
    'L11', 'L12', 'L13', 'L14', 'L15',  # BPF input stage
    'Q1',                               # RF amp
    'X1', 'D1', 'D2', 'D3', 'D4',      # Oscillator & mixer
    'L4', 'L5', 'IC2',                 # PSN network
    'Q5',                              # TX driver
    'T1',                              # Audio transformer
    'Q2', 'Q3', 'Q4', 'Q6', 'Q11',    # RX stages
]

def get_signal_order(cluster):
    """Return the earliest signal-flow position in this cluster."""
    min_order = float('inf')
    for ref in cluster:
        # Extract component base (e.g., Q1 from Q1a)
        base = ''.join([c for c in ref if not c.isdigit()])
        num_str = ''.join([c for c in ref if c.isdigit()])
        if num_str:
            num = int(num_str)
        else:
            num = 0

        # Check if this ref is a key node in signal flow
        for i, flow_ref in enumerate(SIGNAL_FLOW_ORDER):
            if flow_ref in ref or ref in flow_ref:
                min_order = min(min_order, i)

    return min_order if min_order != float('inf') else 999


def main():
    print('Parsing netlist...')
    comp_nets, net_comps = parse_netlist(str(NET_FILE))
    print(f'Found {len(comp_nets)} components, {len(net_comps)} nets')

    board = pcbnew.LoadBoard(str(PCB_FILE))
    pcb_refs = {fp.GetReference() for fp in board.GetFootprints() if not fp.GetReference().startswith('H')}
    print(f'PCB has {len(pcb_refs)} footprints')

    missing = pcb_refs - set(comp_nets.keys())
    if missing:
        print(f'  Missing in netlist: {sorted(missing)[:10]}')

    print('Finding connected clusters...')
    clusters = find_component_clusters(comp_nets, net_comps, max_cluster_size=20)
    clusters.sort(key=get_signal_order)  # Sort by signal flow

    print(f'Found {len(clusters)} component clusters')
    for i, cluster in enumerate(clusters[:10]):
        print(f'  Cluster {i}: {sorted(cluster)}')

    # ────────────────────────────────────────────────────────────────────────
    # Place clusters on board
    # ────────────────────────────────────────────────────────────────────────

    board = pcbnew.LoadBoard(str(PCB_FILE))
    if board is None:
        print('ERROR: cannot load PCB'); return

    # Board grid (adaptive: distribute clusters evenly)
    X_MIN, X_MAX = 5, 145
    Y_MIN, Y_MAX = 5, 95
    BOARD_W = X_MAX - X_MIN
    BOARD_H = Y_MAX - Y_MIN

    # Grid layout: try to fit clusters in a rectangular grid
    n_clusters = len(clusters)
    grid_cols = max(1, int(math.ceil(math.sqrt(n_clusters * BOARD_W / BOARD_H))))
    grid_rows = max(1, (n_clusters + grid_cols - 1) // grid_cols)

    cell_w = BOARD_W / grid_cols
    cell_h = BOARD_H / grid_rows

    placed = 0

    for idx, cluster in enumerate(clusters):
        grid_col = idx % grid_cols
        grid_row = idx // grid_cols

        x1 = X_MIN + grid_col * cell_w
        y1 = Y_MIN + grid_row * cell_h
        x2 = x1 + cell_w
        y2 = y1 + cell_h

        # Place cluster members in this cell
        cell_w_avail = x2 - x1 - 2
        cell_h_avail = y2 - y1 - 2
        refs = sorted(cluster)
        n = len(refs)

        # Packing: arrange in rows of ~3-4 items per row
        items_per_row = max(1, int(math.sqrt(n)))
        for i, ref in enumerate(refs):
            fp = board.FindFootprintByReference(ref)
            if fp is None:
                continue

            row_in_cell = i // items_per_row
            col_in_cell = i % items_per_row

            cell_rows = max(1, (n + items_per_row - 1) // items_per_row)

            cx = x1 + 1 + (col_in_cell + 0.5) * cell_w_avail / items_per_row
            cy = y1 + 1 + (row_in_cell + 0.5) * cell_h_avail / cell_rows

            fp.SetPosition(pcbnew.VECTOR2I(mm(cx), mm(cy)))
            fp.SetOrientationDegrees(0)
            placed += 1

    board.Save(str(PCB_FILE))
    print(f'\nPlaced {placed} components in {len(clusters)} clusters')
    print(f'Saved: {PCB_FILE}')


if __name__ == '__main__':
    main()
