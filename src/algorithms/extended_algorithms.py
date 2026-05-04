"""
扩展算法实现：用于算法对比展示

说明：
- Bellman-Ford 和 SPFA 是最短路径算法。
- PrimMSTBaseline 构造最小生成树并从源点导出树路径，
  其路径代价不保证等于最短路径，仅作为对比基线。
"""
import heapq
import time
from collections import deque
from typing import Dict, List, Tuple


class BellmanFordAlgorithm:
    """Bellman-Ford 单源最短路径算法（支持正权/负权，且此项目使用正权）。"""

    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

    def calculate_shortest_paths(
        self,
        source: int,
        graph: Dict[int, List[Tuple[int, int]]],
    ) -> Dict[int, Tuple[int, List[int]]]:
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

        nodes = list(graph.keys())
        distances = {node: float('inf') for node in nodes}
        predecessor = {}

        if source not in distances:
            distances[source] = 0
            nodes.append(source)

        distances[source] = 0

        # 展开边列表，避免每轮重复构建
        edges = []
        for u, neighbors in graph.items():
            for v, w in neighbors:
                edges.append((u, v, w))

        n = len(nodes)
        for _ in range(max(0, n - 1)):
            self.iterations += 1
            updated = False
            for u, v, w in edges:
                if distances.get(u, float('inf')) == float('inf'):
                    continue
                new_dist = distances[u] + w
                if new_dist < distances.get(v, float('inf')):
                    distances[v] = new_dist
                    predecessor[v] = u
                    self.relaxation_count += 1
                    updated = True
            if not updated:
                break

        # 构造路径
        result = {}
        for node, dist in distances.items():
            if node == source or dist == float('inf'):
                continue

            path = [node]
            curr = node
            seen = set()
            while curr != source and curr in predecessor and curr not in seen:
                seen.add(curr)
                curr = predecessor[curr]
                path.append(curr)
            path.reverse()

            if path and path[0] == source:
                result[node] = (int(dist), path)

        self.visited_nodes = len(result) + 1  # 包含源点
        self.computation_time = time.perf_counter() - start_time
        return result

    def get_statistics(self) -> Dict:
        return {
            'algorithm_name': 'BellmanFord',
            'computation_time': self.computation_time * 1000,
            'visited_nodes': self.visited_nodes,
            'relaxation_count': self.relaxation_count,
            'iterations': self.iterations,
        }


class SPFAAlgorithm:
    """SPFA（队列优化 Bellman-Ford）。"""

    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

    def calculate_shortest_paths(
        self,
        source: int,
        graph: Dict[int, List[Tuple[int, int]]],
    ) -> Dict[int, Tuple[int, List[int]]]:
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

        distances = {node: float('inf') for node in graph.keys()}
        predecessor = {}
        in_queue = {node: False for node in graph.keys()}

        if source not in distances:
            distances[source] = 0
            in_queue[source] = False

        distances[source] = 0
        q = deque([source])
        in_queue[source] = True

        processed = set()

        while q:
            u = q.popleft()
            in_queue[u] = False
            processed.add(u)
            self.iterations += 1

            for v, w in graph.get(u, []):
                new_dist = distances[u] + w
                if new_dist < distances.get(v, float('inf')):
                    distances[v] = new_dist
                    predecessor[v] = u
                    self.relaxation_count += 1
                    if not in_queue.get(v, False):
                        q.append(v)
                        in_queue[v] = True

        result = {}
        for node, dist in distances.items():
            if node == source or dist == float('inf'):
                continue

            path = [node]
            curr = node
            seen = set()
            while curr != source and curr in predecessor and curr not in seen:
                seen.add(curr)
                curr = predecessor[curr]
                path.append(curr)
            path.reverse()

            if path and path[0] == source:
                result[node] = (int(dist), path)

        self.visited_nodes = len(processed)
        self.computation_time = time.perf_counter() - start_time
        return result

    def get_statistics(self) -> Dict:
        return {
            'algorithm_name': 'SPFA',
            'computation_time': self.computation_time * 1000,
            'visited_nodes': self.visited_nodes,
            'relaxation_count': self.relaxation_count,
            'iterations': self.iterations,
        }


class PrimMSTBaseline:
    """Prim 最小生成树基线（非最短路径算法）。"""

    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0
        self.mst_total_cost = 0

    def calculate_shortest_paths(
        self,
        source: int,
        graph: Dict[int, List[Tuple[int, int]]],
    ) -> Dict[int, Tuple[int, List[int]]]:
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0
        self.mst_total_cost = 0

        if source not in graph:
            self.computation_time = time.perf_counter() - start_time
            return {}

        visited = set([source])
        parent = {source: None}
        parent_cost = {source: 0}

        edge_heap = []
        for v, w in graph.get(source, []):
            heapq.heappush(edge_heap, (w, source, v))

        while edge_heap and len(visited) < len(graph):
            self.iterations += 1
            w, u, v = heapq.heappop(edge_heap)
            if v in visited:
                continue

            visited.add(v)
            parent[v] = u
            parent_cost[v] = w
            self.relaxation_count += 1
            self.mst_total_cost += w

            for nv, nw in graph.get(v, []):
                if nv not in visited:
                    heapq.heappush(edge_heap, (nw, v, nv))

        self.visited_nodes = len(visited)

        # 从父节点关系回溯生成路径与树上累计成本
        result = {}
        for node in visited:
            if node == source:
                continue
            path = []
            curr = node
            total_cost = 0
            while curr is not None:
                path.append(curr)
                p = parent.get(curr)
                total_cost += parent_cost.get(curr, 0)
                curr = p
            path.reverse()
            result[node] = (total_cost, path)

        self.computation_time = time.perf_counter() - start_time
        return result

    def get_statistics(self) -> Dict:
        return {
            'algorithm_name': 'PrimMSTBaseline',
            'computation_time': self.computation_time * 1000,
            'visited_nodes': self.visited_nodes,
            'relaxation_count': self.relaxation_count,
            'iterations': self.iterations,
            'mst_total_cost': self.mst_total_cost,
        }


class FloydWarshallAlgorithm:
    """Floyd-Warshall 全源最短路径，最终返回指定源点到其余节点路径。"""

    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

    def calculate_shortest_paths(
        self,
        source: int,
        graph: Dict[int, List[Tuple[int, int]]],
    ) -> Dict[int, Tuple[int, List[int]]]:
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

        nodes = sorted(set(graph.keys()))
        if source not in nodes:
            nodes.append(source)
            nodes.sort()

        n = len(nodes)
        idx = {node: i for i, node in enumerate(nodes)}

        inf = float('inf')
        dist = [[inf] * n for _ in range(n)]
        nxt = [[None] * n for _ in range(n)]

        for i in range(n):
            dist[i][i] = 0
            nxt[i][i] = i

        for u, neighbors in graph.items():
            ui = idx[u]
            for v, w in neighbors:
                vi = idx[v]
                if w < dist[ui][vi]:
                    dist[ui][vi] = w
                    nxt[ui][vi] = vi

        for k in range(n):
            for i in range(n):
                dik = dist[i][k]
                if dik == inf:
                    continue
                for j in range(n):
                    self.iterations += 1
                    dkj = dist[k][j]
                    if dkj == inf:
                        continue
                    nd = dik + dkj
                    if nd < dist[i][j]:
                        dist[i][j] = nd
                        nxt[i][j] = nxt[i][k]
                        self.relaxation_count += 1

        result = {}
        si = idx[source]
        for node in nodes:
            if node == source:
                continue
            ti = idx[node]
            if dist[si][ti] == inf or nxt[si][ti] is None:
                continue

            path_idx = [si]
            cur = si
            guard = 0
            while cur != ti and guard <= n:
                cur = nxt[cur][ti]
                if cur is None:
                    break
                path_idx.append(cur)
                guard += 1

            if not path_idx or path_idx[-1] != ti:
                continue

            path = [nodes[i] for i in path_idx]
            result[node] = (int(dist[si][ti]), path)

        self.visited_nodes = len(result) + 1
        self.computation_time = time.perf_counter() - start_time
        return result

    def get_statistics(self) -> Dict:
        return {
            'algorithm_name': 'FloydWarshall',
            'computation_time': self.computation_time * 1000,
            'visited_nodes': self.visited_nodes,
            'relaxation_count': self.relaxation_count,
            'iterations': self.iterations,
        }


class AStarAllTargetsAlgorithm:
    """A*（单源到多目标实现：对每个目标执行一次 A*）。"""

    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

    def _build_reverse_graph(
        self,
        graph: Dict[int, List[Tuple[int, int]]],
    ) -> Dict[int, List[int]]:
        reverse = {node: [] for node in graph.keys()}
        for u, neighbors in graph.items():
            for v, _ in neighbors:
                reverse.setdefault(v, []).append(u)
        return reverse

    def _hop_heuristic(
        self,
        reverse_graph: Dict[int, List[int]],
        min_edge_cost: int,
        target: int,
    ) -> Dict[int, int]:
        # 使用“最少跳数 * 最小边权”的可采纳启发式
        hops = {target: 0}
        q = deque([target])
        while q:
            curr = q.popleft()
            for prev in reverse_graph.get(curr, []):
                if prev not in hops:
                    hops[prev] = hops[curr] + 1
                    q.append(prev)
        return {node: hop * min_edge_cost for node, hop in hops.items()}

    def _astar_one_target(
        self,
        source: int,
        target: int,
        graph: Dict[int, List[Tuple[int, int]]],
        heuristic_map: Dict[int, int],
    ):
        open_heap = []
        g_score = {source: 0}
        parent = {}
        visited = set()

        h0 = heuristic_map.get(source, 0)
        heapq.heappush(open_heap, (h0, 0, source))

        while open_heap:
            self.iterations += 1
            _, g_curr, node = heapq.heappop(open_heap)
            if node in visited:
                continue
            visited.add(node)

            if node == target:
                path = [node]
                while path[-1] in parent:
                    path.append(parent[path[-1]])
                path.reverse()
                self.visited_nodes += len(visited)
                return g_curr, path

            for nb, w in graph.get(node, []):
                ng = g_curr + w
                if ng < g_score.get(nb, float('inf')):
                    g_score[nb] = ng
                    parent[nb] = node
                    self.relaxation_count += 1
                    f = ng + heuristic_map.get(nb, 0)
                    heapq.heappush(open_heap, (f, ng, nb))

        self.visited_nodes += len(visited)
        return None, []

    def calculate_shortest_paths(
        self,
        source: int,
        graph: Dict[int, List[Tuple[int, int]]],
    ) -> Dict[int, Tuple[int, List[int]]]:
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0

        if source not in graph:
            self.computation_time = time.perf_counter() - start_time
            return {}

        min_edge_cost = 1
        for neighbors in graph.values():
            for _, w in neighbors:
                if w > 0:
                    min_edge_cost = min(min_edge_cost, w)

        reverse_graph = self._build_reverse_graph(graph)

        result = {}
        for target in graph.keys():
            if target == source:
                continue
            heuristic_map = self._hop_heuristic(reverse_graph, min_edge_cost, target)
            cost, path = self._astar_one_target(source, target, graph, heuristic_map)
            if cost is not None and path:
                result[target] = (int(cost), path)

        self.computation_time = time.perf_counter() - start_time
        return result

    def get_statistics(self) -> Dict:
        return {
            'algorithm_name': 'AStarAllTargets',
            'computation_time': self.computation_time * 1000,
            'visited_nodes': self.visited_nodes,
            'relaxation_count': self.relaxation_count,
            'iterations': self.iterations,
        }
