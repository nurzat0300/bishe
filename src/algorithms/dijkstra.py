"""
Dijkstra最短路径算法实现
"""
import heapq
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import time

class DijkstraAlgorithm:
    """Dijkstra算法实现"""
    
    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.iterations = 0
    
    def calculate_shortest_paths(self, 
                                 source: int, 
                                 graph: Dict[int, List[Tuple[int, int]]]) -> Dict[int, Tuple[int, List[int]]]:
        """
        使用Dijkstra算法计算最短路径
        
        Args:
            source: 源节点ID
            graph: 邻接表形式的图 {node: [(neighbor, cost), ...]}
        
        Returns:
            {destination: (cost, path)} 字典
        """
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.iterations = 0
        
        # 距离表：{node: min_cost}
        distances = {source: 0}
        
        # 路径表：{node: [path]}
        paths = {source: [source]}
        
        # 优先队列：(cost, node)
        pq = [(0, source)]
        
        # 已访问节点集合
        visited = set()
        
        while pq:
            self.iterations += 1
            curr_cost, curr_node = heapq.heappop(pq)
            
            # 跳过已访问节点
            if curr_node in visited:
                continue
            
            visited.add(curr_node)
            self.visited_nodes += 1
            
            # 已经找到更短路径，跳过
            if curr_cost > distances.get(curr_node, float('inf')):
                continue
            
            # 处理所有邻接节点
            if curr_node in graph:
                for neighbor, cost in graph[curr_node]:
                    new_cost = curr_cost + cost
                    
                    # 找到更短路径
                    if neighbor not in distances or new_cost < distances[neighbor]:
                        distances[neighbor] = new_cost
                        paths[neighbor] = paths[curr_node] + [neighbor]
                        heapq.heappush(pq, (new_cost, neighbor))
        
        self.computation_time = time.perf_counter() - start_time
        
        # 构造返回结果
        result = {}
        for dest in distances:
            if dest != source:
                result[dest] = (distances[dest], paths.get(dest, []))
        
        return result
    
    def get_statistics(self) -> Dict:
        """获取算法统计信息"""
        return {
            'algorithm_name': 'Dijkstra',
            'computation_time': self.computation_time * 1000,  # 毫秒
            'visited_nodes': self.visited_nodes,
            'iterations': self.iterations
        }


class DijkstraWithPriorityQueue(DijkstraAlgorithm):
    """使用优先队列优化的Dijkstra算法"""
    
    def calculate_shortest_paths(self, 
                                 source: int, 
                                 graph: Dict[int, List[Tuple[int, int]]]) -> Dict[int, Tuple[int, List[int]]]:
        """
        优化版的Dijkstra算法（已使用优先队列）
        """
        return super().calculate_shortest_paths(source, graph)
