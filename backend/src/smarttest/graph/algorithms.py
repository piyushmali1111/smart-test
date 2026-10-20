"""Core Graph Algorithms implemented by hand for DAA project.

Includes:
- Multi-source Breadth-First Search (BFS) for shortest path distance
- Iterative Depth-First Search (DFS) for reachability
- Iterative Tarjan's Strongly Connected Components (SCC)
- Kahn's Algorithm for Topological Sort and Longest-Path Level calculation
"""

from collections import deque
from typing import Dict, List, Set, Tuple, Optional


def bfs_distances(
    adj: Dict[str, List[str]], sources: List[str]
) -> Dict[str, int]:
    """Computes shortest path distances from a set of source nodes using BFS.

    Algorithm: Multi-source Breadth-First Search
    Time Complexity: O(V + E) where V is the number of vertices and E is the number of edges.
    Space Complexity: O(V) for the queue and distance dictionary.

    Args:
        adj: Adjacency list mapping node -> list of outgoing neighbor nodes.
        sources: List of source node IDs starting at distance 0.

    Returns:
        Dictionary mapping reachable node -> shortest distance from nearest source.
    """
    distances: Dict[str, int] = {}
    queue: deque[Tuple[str, int]] = deque()

    for src in sources:
        if src in adj or any(src in neighbors for neighbors in adj.values()):
            distances[src] = 0
            queue.append((src, 0))

    while queue:
        curr, dist = queue.popleft()
        for neighbor in adj.get(curr, []):
            if neighbor not in distances:
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))

    return distances


def dfs_reachable(adj: Dict[str, List[str]], start: str) -> Set[str]:
    """Computes all reachable nodes from a start node using an iterative DFS.

    Algorithm: Iterative Depth-First Search
    Time Complexity: O(V + E) where V is reachable vertices and E is outgoing edges.
    Space Complexity: O(V) for the stack and visited set.

    Args:
        adj: Adjacency list mapping node -> list of outgoing neighbor nodes.
        start: Starting node ID.

    Returns:
        Set of all node IDs reachable from `start` (including `start` itself).
    """
    visited: Set[str] = set()
    stack: List[str] = [start]

    while stack:
        curr = stack.pop()
        if curr not in visited:
            visited.add(curr)
            for neighbor in reversed(adj.get(curr, [])):
                if neighbor not in visited:
                    stack.append(neighbor)

    return visited


def tarjan_scc(
    nodes: List[str], adj: Dict[str, List[str]]
) -> List[List[str]]:
    """Finds all Strongly Connected Components (SCC) using Tarjan's algorithm.

    Implemented iteratively using an explicit call stack to eliminate Python
    recursion depth limits on large codebases.

    Algorithm: Tarjan's SCC (Iterative DFS)
    Time Complexity: O(V + E) where V is the number of vertices and E is the number of edges.
    Space Complexity: O(V) for indexing, lowlink tracking, and DFS stack.

    Args:
        nodes: Complete list of all node IDs in the graph.
        adj: Adjacency list mapping node -> list of outgoing neighbor nodes.

    Returns:
        List of SCC components, where each component is a list of node IDs.
    """
    index = 0
    indices: Dict[str, int] = {}
    lowlinks: Dict[str, int] = {}
    on_stack: Set[str] = set()
    stack: List[str] = []
    sccs: List[List[str]] = []

    for root in nodes:
        if root in indices:
            continue

        # Each element in call_stack represents: (node, neighbor_index)
        call_stack: List[Tuple[str, int]] = [(root, 0)]
        indices[root] = index
        lowlinks[root] = index
        index += 1
        stack.append(root)
        on_stack.add(root)

        while call_stack:
            v, edge_idx = call_stack[-1]
            neighbors = adj.get(v, [])

            if edge_idx < len(neighbors):
                w = neighbors[edge_idx]
                call_stack[-1] = (v, edge_idx + 1)

                if w not in indices:
                    indices[w] = index
                    lowlinks[w] = index
                    index += 1
                    stack.append(w)
                    on_stack.add(w)
                    call_stack.append((w, 0))
                elif w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])
            else:
                call_stack.pop()
                if call_stack:
                    parent, _ = call_stack[-1]
                    lowlinks[parent] = min(lowlinks[parent], lowlinks[v])

                if lowlinks[v] == indices[v]:
                    component: List[str] = []
                    while True:
                        node = stack.pop()
                        on_stack.remove(node)
                        component.append(node)
                        if node == v:
                            break
                    sccs.append(component)

    return sccs


def kahn_topological_sort(
    nodes: List[str], adj: Dict[str, List[str]]
) -> Tuple[List[str], Dict[str, int]]:
    """Performs topological sort using Kahn's algorithm and computes topological levels.

    Algorithm: Kahn's Algorithm with Longest-Path Level calculation on DAG.
    Time Complexity: O(V + E).
    Space Complexity: O(V + E) for in-degree tracking and queues.

    The topological level of a node is defined as the length of the longest path
    from the node to a sink (leaf) node in the DAG. Sink nodes have level 0.

    Args:
        nodes: Nodes in the DAG.
        adj: Adjacency list of the DAG (must be cycle-free).

    Returns:
        Tuple of (ordered_nodes, node_to_level_map).

    Raises:
        ValueError: If a cycle exists in the graph.
    """
    in_degree: Dict[str, int] = {node: 0 for node in nodes}
    for u in nodes:
        for v in adj.get(u, []):
            if v in in_degree:
                in_degree[v] += 1

    queue: deque[str] = deque([node for node in nodes if in_degree[node] == 0])
    ordered: List[str] = []

    while queue:
        u = queue.popleft()
        ordered.append(u)
        for v in adj.get(u, []):
            if v in in_degree:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

    if len(ordered) != len(nodes):
        raise ValueError("Cycle detected in graph; topological sort cannot be completed.")

    # Compute topological levels (longest path to sink) by working backward
    levels: Dict[str, int] = {node: 0 for node in nodes}
    for u in reversed(ordered):
        for v in adj.get(u, []):
            if v in levels:
                levels[u] = max(levels[u], levels[v] + 1)

    return ordered, levels
