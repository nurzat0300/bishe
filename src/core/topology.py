"""
拓扑管理模块
"""
from typing import Dict, List, Set, Tuple, Optional
import threading
from .constants import Link, LinkState, Constants
try:
    import networkx as nx
except ImportError:
    nx = None

class TopologyDB:
    """拓扑数据库"""
    
    def __init__(self):
        # 使用NetworkX无向图表示拓扑
        self.graph = nx.Graph()
        self._lock = threading.RLock()
        # {router_id: set(neighbor_ids)}
        self._adjacency: Dict[int, Set[int]] = {}
        # {(src, dest): cost}
        self._link_costs: Dict[Tuple[int, int], int] = {}
    
    def add_router(self, router_id: int):
        """添加路由器节点"""
        with self._lock:
            if router_id not in self.graph.nodes:
                self.graph.add_node(router_id)
                self._adjacency[router_id] = set()
    
    def add_link(self, src: int, dest: int, cost: int = 1):
        """添加双向链路"""
        with self._lock:
            self.add_router(src)
            self.add_router(dest)

            self.graph.add_edge(src, dest, weight=cost)
            self._adjacency[src].add(dest)
            self._adjacency[dest].add(src)

            key1 = (min(src, dest), max(src, dest))
            self._link_costs[key1] = cost
    
    def remove_link(self, src: int, dest: int):
        """移除链路"""
        with self._lock:
            if self.graph.has_edge(src, dest):
                self.graph.remove_edge(src, dest)
                self._adjacency[src].discard(dest)
                self._adjacency[dest].discard(src)

                key = (min(src, dest), max(src, dest))
                self._link_costs.pop(key, None)
    
    def get_neighbors(self, router_id: int) -> Set[int]:
        """获取邻接路由器"""
        with self._lock:
            return set(self._adjacency.get(router_id, set()))
    
    def get_link_cost(self, src: int, dest: int) -> int:
        """获取链路成本"""
        with self._lock:
            if self.graph.has_edge(src, dest):
                return self.graph[src][dest]['weight']
            return Constants.INFINITY
    
    def get_all_routers(self) -> List[int]:
        """获取所有路由器节点"""
        with self._lock:
            return list(self.graph.nodes)
    
    def is_connected(self) -> bool:
        """判断图是否连通"""
        with self._lock:
            return nx.is_connected(self.graph)
    
    def get_path_if_exists(self, src: int, dest: int) -> Optional[List[int]]:
        """获取最短路径（如果存在）"""
        with self._lock:
            try:
                if src in self.graph and dest in self.graph:
                    return nx.shortest_path(self.graph, src, dest, weight='weight')
            except (nx.NoPath, nx.NodeNotFound):
                pass
            return None
    
    def clear(self):
        """清空拓扑"""
        with self._lock:
            self.graph.clear()
            self._adjacency.clear()
            self._link_costs.clear()


class RoutingTable:
    """路由表"""
    
    def __init__(self, router_id: int):
        self.router_id = router_id
        self._lock = threading.RLock()
        # {dest_router_id: (next_hop, cost, full_path)}
        self._routes: Dict[int, Tuple[int, int, List[int]]] = {}
    
    def update_route(self, destination: int, next_hop: int, cost: int, path: List[int]):
        """更新路由表项"""
        with self._lock:
            self._routes[destination] = (next_hop, cost, path)
    
    def get_next_hop(self, destination: int) -> Optional[int]:
        """获取下一跳"""
        with self._lock:
            if destination in self._routes:
                return self._routes[destination][0]
            return None
    
    def get_route(self, destination: int) -> Optional[Tuple[int, int, List[int]]]:
        """获取完整路由信息"""
        with self._lock:
            return self._routes.get(destination)
    
    def get_all_routes(self) -> Dict[int, Tuple[int, int, List[int]]]:
        """获取所有路由"""
        with self._lock:
            return self._routes.copy()
    
    def clear(self):
        """清空路由表"""
        with self._lock:
            self._routes.clear()
