import sys
from .routing import Routing


class DijkstraRelaxing(Routing):
    """
    Generalizes LatencyRelaxing and TwoHopRelaxing into a proper shortest-
    path algorithm. Those strategies hardcode a fixed number of
    intermediate hops (one or two), so they miss genuinely shorter paths
    on larger topologies and get combinatorially expensive as hop count
    grows. This strategy runs Dijkstra's algorithm over the RTT matrix
    instead, finding the true lowest-latency path regardless of how many
    hops it takes, with no fixed depth limit.
    """

    def __init__(self, network_manager, datapaths):
        super().__init__(network_manager, datapaths)

    def get_optimal_route(self, source_dpid, target_dpid):
        source_index = self.link_to_index[source_dpid]
        target_index = self.link_to_index[target_dpid]
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
                edge_weight = self.rtt_matrix[current][neighbor]
                if edge_weight == sys.maxsize:
                    continue
                new_distance = distance[current] + edge_weight
                if new_distance < distance[neighbor]:
                    distance[neighbor] = new_distance
                    previous[neighbor] = current

        path_indices = []
        step = target_index
        while step is not None:
            path_indices.append(step)
            step = previous[step]
        path_indices.reverse()

        if not path_indices or path_indices[0] != source_index:
            return [source_dpid, target_dpid]

        return [self.index_to_link[i] for i in path_indices]

    def update_rtt_matrix(self, latency_results):
        for measurement in latency_results:
            source_dpid = measurement.src
            source_index = self.link_to_index[source_dpid]
            latency_data = measurement.metric
            for dpid, latency in latency_data.items():
                target_index = self.link_to_index[int(dpid)]
                self.rtt_matrix[source_index][target_index] = latency