"""Dependency Graph model representing functions, calls, SCC condensation, and reachability."""

from typing import Dict, List, Set, Tuple, Any, Optional
from smarttest.graph.algorithms import (
    bfs_distances,
    dfs_reachable,
    tarjan_scc,
    kahn_topological_sort,
)


class DependencyGraph:
    """Manages the static call graph, reverse reachability, SCCs, and topological levels."""

    def __init__(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, str]],
    ):
        self.raw_nodes = nodes
        self.node_ids = [n["id"] for n in nodes]
        self.node_meta = {n["id"]: n for n in nodes}

        # Forward adjacency: caller -> list of callees (A uses B)
        self.adj: Dict[str, List[str]] = {nid: [] for nid in self.node_ids}
        # Reverse adjacency: callee -> list of callers (B is called by A)
        self.rev_adj: Dict[str, List[str]] = {nid: [] for nid in self.node_ids}

        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            if src in self.adj and tgt in self.adj:
                self.adj[src].append(tgt)
                self.rev_adj[tgt].append(src)

        # 1. Compute SCCs using Tarjan's algorithm
        self.sccs: List[List[str]] = tarjan_scc(self.node_ids, self.adj)

        # Multi-node cycles only (for API sccGroups)
        self.scc_groups: List[List[str]] = [scc for scc in self.sccs if len(scc) > 1]

        # Map each node to its SCC index
        self.node_to_scc: Dict[str, int] = {}
        for scc_idx, comp in enumerate(self.sccs):
            for nid in comp:
                self.node_to_scc[nid] = scc_idx

        # 2. Build Condensed DAG: scc_u -> set of scc_v
        num_sccs = len(self.sccs)
        scc_nodes = [f"scc_{i}" for i in range(num_sccs)]
        condensed_adj: Dict[str, List[str]] = {s: [] for s in scc_nodes}
        condensed_rev_adj: Dict[str, List[str]] = {s: [] for s in scc_nodes}

        for u in self.node_ids:
            u_scc = f"scc_{self.node_to_scc[u]}"
            for v in self.adj.get(u, []):
                v_scc = f"scc_{self.node_to_scc[v]}"
                if u_scc != v_scc:
                    if v_scc not in condensed_adj[u_scc]:
                        condensed_adj[u_scc].append(v_scc)
                    if u_scc not in condensed_rev_adj[v_scc]:
                        condensed_rev_adj[v_scc].append(u_scc)

        self.condensed_adj = condensed_adj
        self.condensed_rev_adj = condensed_rev_adj

        # 3. Compute topological levels on the condensed DAG
        try:
            _, scc_levels = kahn_topological_sort(scc_nodes, self.condensed_adj)
            self.node_levels = {
                nid: scc_levels.get(f"scc_{self.node_to_scc[nid]}", 0)
                for nid in self.node_ids
            }
        except ValueError:
            # Fallback if condensation somehow had edge error
            self.node_levels = {nid: 0 for nid in self.node_ids}

        for n in self.raw_nodes:
            n["topoLevel"] = self.node_levels.get(n["id"], 0)

    def get_affected_and_distances(
        self, changed_ids: List[str]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """Finds all affected functions and their condensed graph distances.

        Traverses on the reverse condensed graph starting from the SCCs of changed_ids.
        Returns:
            affected_list: list of {"id": node_id, "distance": dist} sorted by distance.
            distance_map: dict of node_id -> distance.
        """
        valid_changed = [c for c in changed_ids if c in self.node_to_scc]
        if not valid_changed:
            return [], {}

        source_sccs = list({f"scc_{self.node_to_scc[c]}" for c in valid_changed})
        # BFS on condensed_rev_adj
        scc_distances = bfs_distances(self.condensed_rev_adj, source_sccs)

        affected: List[Dict[str, Any]] = []
        distance_map: Dict[str, int] = {}

        for nid in self.node_ids:
            scc_id = f"scc_{self.node_to_scc[nid]}"
            if scc_id in scc_distances:
                dist = scc_distances[scc_id]
                affected.append({"id": nid, "distance": dist})
                distance_map[nid] = dist

        affected.sort(key=lambda x: (x["distance"], x["id"]))
        return affected, distance_map

    def get_blast_radius(self, func_id: str) -> int:
        """Computes blast radius |A({func_id})| for a single function."""
        affected, _ = self.get_affected_and_distances([func_id])
        return len(affected)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes graph to dict format matching the API contract."""
        return {
            "nodes": self.raw_nodes,
            "edges": [
                {"source": u, "target": v}
                for u, callees in self.adj.items()
                for v in callees
            ],
        }
