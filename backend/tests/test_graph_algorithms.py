"""Verification of hand-written graph algorithms against NetworkX on 100+ random graphs."""

import random
import pytest
import networkx as nx

from smarttest.graph.algorithms import (
    bfs_distances,
    dfs_reachable,
    tarjan_scc,
    kahn_topological_sort,
)


def generate_random_directed_graph(n: int, p: float, rng: random.Random):
    nodes = [f"v{i}" for i in range(n)]
    adj = {u: [] for u in nodes}
    edges = []
    for u in nodes:
        for v in nodes:
            if u != v and rng.random() < p:
                adj[u].append(v)
                edges.append((u, v))
    return nodes, adj, edges


def test_tarjan_scc_matches_networkx_100_graphs():
    rng = random.Random(42)
    for trial in range(100):
        n = rng.randint(5, 30)
        p = rng.uniform(0.05, 0.35)
        nodes, adj, edges = generate_random_directed_graph(n, p, rng)

        # Hand-written Tarjan SCC
        my_sccs = tarjan_scc(nodes, adj)
        my_scc_sets = {frozenset(comp) for comp in my_sccs}

        # NetworkX reference
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx_scc_sets = {frozenset(comp) for comp in nx.strongly_connected_components(G)}

        assert my_scc_sets == nx_scc_sets, f"Failed on trial {trial} with n={n}, p={p:.2f}"


def test_bfs_distances_matches_networkx_100_graphs():
    rng = random.Random(101)
    for trial in range(100):
        n = rng.randint(5, 25)
        p = rng.uniform(0.1, 0.4)
        nodes, adj, edges = generate_random_directed_graph(n, p, rng)

        src = rng.choice(nodes)

        # Hand-written BFS
        my_dist = bfs_distances(adj, [src])

        # NetworkX reference
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        nx_dist = dict(nx.single_source_shortest_path_length(G, src))

        assert my_dist == nx_dist, f"BFS mismatch on trial {trial}"


def test_dfs_reachable_matches_networkx_100_graphs():
    rng = random.Random(202)
    for trial in range(100):
        n = rng.randint(5, 25)
        p = rng.uniform(0.1, 0.4)
        nodes, adj, edges = generate_random_directed_graph(n, p, rng)

        src = rng.choice(nodes)

        # Hand-written DFS
        my_reachable = dfs_reachable(adj, src)

        # NetworkX reference
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)
        nx_reachable = nx.descendants(G, src) | {src}

        assert my_reachable == nx_reachable, f"DFS mismatch on trial {trial}"


def test_kahn_topological_sort_on_dags():
    rng = random.Random(303)
    for trial in range(50):
        n = rng.randint(6, 25)
        # Create strict DAG: edges only from lower index to higher index
        nodes = [f"v{i}" for i in range(n)]
        adj = {u: [] for u in nodes}
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.25:
                    adj[nodes[i]].append(nodes[j])

        order, levels = kahn_topological_sort(nodes, adj)

        # Every edge u -> v must appear with pos(u) < pos(v)
        pos = {node: idx for idx, node in enumerate(order)}
        for u in nodes:
            for v in adj[u]:
                assert pos[u] < pos[v]

        # Verify topological levels: sink nodes have level 0
        for u in nodes:
            if not adj[u]:
                assert levels[u] == 0
            else:
                expected_min_level = max(levels[v] for v in adj[u]) + 1
                assert levels[u] == expected_min_level


def test_kahn_rejects_cycles():
    nodes = ["A", "B", "C"]
    adj = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
    }
    with pytest.raises(ValueError, match="Cycle detected"):
        kahn_topological_sort(nodes, adj)
