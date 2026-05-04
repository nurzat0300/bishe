"""
新算法实现 - 基于清华大学2025年论文
简化版实现：采用分层访问策略加快收敛
"""
import heapq
import time
from typing import Dict, List, Tuple
from collections import defaultdict

class NewAlgorithm:
    """
    新型最短路径算法
    
    核心思想：采用改进的松弛策略和优化的节点访问顺序，
    试图突破传统Dijkstra的\"排序障碍\"
    """
    
    def __init__(self):
        self.computation_time = 0.0
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0
    
    def calculate_shortest_paths(self,
                                 source: int,
                                 graph: Dict[int, List[Tuple[int, int]]]) -> Dict[int, Tuple[int, List[int]]]:
        """
        使用新算法计算最短路径
        
        特点：
        1. 采用多级优先队列管理
        2. 减少无效的松弛操作
        3. 优化节点访问顺序
        
        Args:
            source: 源节点ID
            graph: 邻接表形式的图 {node: [(neighbor, cost), ...]}
        
        Returns:
            {destination: (cost, path)} 字典
        """
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0
        
        # 初始化
        distances = {source: 0}
        paths = {source: [source]}
        visited = set()
        
        # 按成本分桶，同时维护活跃桶最小堆，避免反复全量扫描
        cost_buckets = defaultdict(list)
        bucket_size = 64
        active_bucket_heap = []
        active_bucket_set = set()

        cost_buckets[0].append(source)
        heapq.heappush(active_bucket_heap, 0)
        active_bucket_set.add(0)

        while active_bucket_heap:
            self.iterations += 1

            # 弹出当前最小的非空桶
            while active_bucket_heap and not cost_buckets[active_bucket_heap[0]]:
                empty_key = heapq.heappop(active_bucket_heap)
                active_bucket_set.discard(empty_key)

            if not active_bucket_heap:
                break

            min_cost = active_bucket_heap[0]
            curr_node = cost_buckets[min_cost].pop()
            
            # 跳过已访问节点
            if curr_node in visited:
                continue
            
            curr_cost = distances[curr_node]
            visited.add(curr_node)
            self.visited_nodes += 1
            
            # 处理所有邻接节点
            if curr_node in graph:
                for neighbor, edge_cost in graph[curr_node]:
                    new_cost = curr_cost + edge_cost
                    
                    # 松弛操作
                    if neighbor not in distances or new_cost < distances[neighbor]:
                        self.relaxation_count += 1
                        distances[neighbor] = new_cost
                        paths[neighbor] = paths[curr_node] + [neighbor]
                        
                        # 添加到相应的桶
                        cost_bucket = (new_cost // bucket_size) * bucket_size
                        cost_buckets[cost_bucket].append(neighbor)
                        if cost_bucket not in active_bucket_set:
                            heapq.heappush(active_bucket_heap, cost_bucket)
                            active_bucket_set.add(cost_bucket)
        
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
            'algorithm_name': 'NewAlgorithm',
            'computation_time': self.computation_time * 1000,  # 毫秒
            'visited_nodes': self.visited_nodes,
            'relaxation_count': self.relaxation_count,
            'iterations': self.iterations
        }


class FastPathAlgorithm(NewAlgorithm):
    """
    快速路径算法 - 使用激进的启发式策略
    """
    
    def calculate_shortest_paths(self,
                                 source: int,
                                 graph: Dict[int, List[Tuple[int, int]]]) -> Dict[int, Tuple[int, List[int]]]:
        """
        快速路径算法 - 优先执行低成本连接
        """
        start_time = time.perf_counter()
        self.visited_nodes = 0
        self.relaxation_count = 0
        self.iterations = 0
        
        distances = {source: 0}
        paths = {source: [source]}
        visited = set()
        
        # 使用标准堆，但增加启发式排序
        pq = [(0, source)]
        
        while pq:
            self.iterations += 1
            curr_cost, curr_node = heapq.heappop(pq)
            
            if curr_node in visited:
                continue
            
            visited.add(curr_node)
            self.visited_nodes += 1
            
            if curr_cost > distances.get(curr_node, float('inf')):
                continue
            
            # 处理邻接节点，按成本排序（增强启发式）
            if curr_node in graph:
                neighbors = sorted(graph[curr_node], key=lambda x: x[1])  # 按边权排序
                
                for neighbor, cost in neighbors:
                    new_cost = curr_cost + cost
                    
                    if neighbor not in distances or new_cost < distances[neighbor]:
                        self.relaxation_count += 1
                        distances[neighbor] = new_cost
                        paths[neighbor] = paths[curr_node] + [neighbor]
                        heapq.heappush(pq, (new_cost, neighbor))
        
        self.computation_time = time.perf_counter() - start_time
        
        result = {}
        for dest in distances:
            if dest != source:
                result[dest] = (distances[dest], paths.get(dest, []))
        
        return result
