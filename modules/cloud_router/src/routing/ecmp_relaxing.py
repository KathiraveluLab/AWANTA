import sys
from .routing import Routing


class ECMPRelaxing(Routing):
    """
    Finds multiple near-equal-cost paths between two switches and assigns
    each a traffic-split weight, instead of always committing all traffic
    to a single "best" path. This is useful once a topology has more than
    one genuinely comparable route available: splitting load across them
    can use available capacity better than funneling everything through
    whichever single path happened to win by a small margin.

    Path discovery is a simplified approach inspired by Yen's k-shortest-
    paths algorithm: find the shortest path via Dijkstra, then repeatedly
    exclude one edge from an already-found path and re-run Dijkstra to
    discover an alternate. An alternate is only kept if its total cost is
    within `tolerance` of the shortest path's cost, so a much worse path
    never gets a meaningful share of traffic.

    get_optimal_route() still returns a single best path, keeping this
    strategy fully compatible with the existing single-path CloudRouter/
    controller flow-installation code. Multi-path behavior is exposed
    separately through get_k_shortest_paths(), for future integration with
    weighted OpenFlow group tables (OFPGT_SELECT), which requires a live
    Mininet/Ryu environment to install and verify.
    """

    def __init__(self, network_manager, datapaths):
        super().__init__(network_manager, datapaths)

    def _dijkstra(self, source_index, target_index, excluded_edges=None):
        excluded_edges = excluded_edges or set()
        n = len(self.rtt_matrix)
        distance = [sys.maxsize] * n
        previous = [None] * n
        visited = [False] * n
        distance[source_index] = 0

        for _ in range(n):
            current = None
            current_distance = sys.maxsize
            for i in range(n):
                if not visited[i] and distance[i] < current_distance:
                    current = i
                    current_distance = distance[i]
            if current is None:
                break
            visited[current] = True
            if current == target_index:
                break
            for neighbor in range(n):
                if visited[neighbor] or neighbor == current:
                    continue
                if (current, neighbor) in excluded_edges:
                    continue
                weight = self.rtt_matrix[current][neighbor]
                if weight == sys.maxsize:
                    continue
                new_distance = distance[current] + weight
                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    previous[neighbor] = current

        path = []
        step = target_index
        while step is not None:
            path.append(step)
            step = previous[step]
        path.reverse()

        if not path or path[0] != source_index:
            return None, sys.maxsize
        return path, distance[target_index]

    def get_k_shortest_paths(self, source_dpid, target_dpid, k=2, tolerance=0.15):
        """
        Returns up to k paths as a list of (dpid_path, weight) tuples,
        where weights are proportional to inverse path cost and sum to 1.0.
        Only paths within `tolerance` (fractional) of the best path's cost
        are included.
        """
        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]

        best_path, best_cost = self._dijkstra(source_index, target_index)
        if best_path is None:
            return [([source_dpid, target_dpid], 1.0)]

        results = [(best_path, best_cost)]
        seen_paths = {tuple(best_path)}
        excluded_edges = set()
        candidate_paths = [best_path]

        while len(results) < k and candidate_paths:
            path_to_branch = candidate_paths.pop(0)
            for i in range(len(path_to_branch) - 1):
                edge = (path_to_branch[i], path_to_branch[i + 1])
                trial_excluded = excluded_edges | {edge}
                alt_path, alt_cost = self._dijkstra(source_index, target_index, trial_excluded)

                if alt_path is None or tuple(alt_path) in seen_paths:
                    continue
                if alt_cost <= best_cost * (1 + tolerance):
                    results.append((alt_path, alt_cost))
                    seen_paths.add(tuple(alt_path))
                    candidate_paths.append(alt_path)
                    excluded_edges.add(edge)
                if len(results) >= k:
                    break

        total_inverse_cost = sum((1.0 / cost) if cost > 0 else 1.0 for _, cost in results)
        weighted_paths = []
        for path_indices, cost in results:
            dpids = [self.index_to_link[i] for i in path_indices]
            weight = ((1.0 / cost) if cost > 0 else 1.0) / total_inverse_cost
            weighted_paths.append((dpids, weight))
        return weighted_paths

    def get_optimal_route(self, source_dpid, target_dpid):
        # Single-path interface, kept compatible with existing CloudRouter
        # usage: always returns just the best path.
        weighted_paths = self.get_k_shortest_paths(source_dpid, target_dpid, k=1)
        return weighted_paths[0][0]

    def update_rtt_matrix(self, latency_results):
        for measurement in latency_results:
            source_dpid = measurement.src
            source_index = self.link_to_index[source_dpid]
            latency_data = measurement.metric
            for dpid, latency in latency_data.items():
                target_index = self.link_to_index[int(dpid)]
                self.rtt_matrix[source_index][target_index] = latency