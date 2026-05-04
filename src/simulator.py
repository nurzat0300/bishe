"""
网络仿真系统主程序
"""
import sys
import json
import os
import logging
import time
from typing import Dict, List, Optional, TYPE_CHECKING
from pathlib import Path
from threading import Event

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)

logger = logging.getLogger('Simulator')

if TYPE_CHECKING:
    from src.core.router import Router


class RoutingSimulator:
    """链路状态路由协议仿真系统"""
    
    def __init__(self, config_file: str = None):
        """初始化仿真系统"""
        self.routers: Dict[int, 'Router'] = {}
        self.config_file = config_file or 'config/network_topology.json'
        self.running = False
        self._stop_event = Event()
        self.logger = logger

    def _get_runtime_profile(self, router_count: int) -> Dict:
        """根据拓扑规模返回运行时参数配置。"""
        # 默认配置（小中拓扑）
        profile = {
            'lsa_send_interval': 5.0,
            'heartbeat_interval': 0.8,
            'heartbeat_timeout_threshold': 3,
            'failure_detection_silence_seconds': 2.0,
            'spf_min_interval': 0.2,
            'log_level': logging.INFO,
        }

        # 50节点及以上采用稳态参数，减少误判与LSA风暴
        if router_count >= 50:
            profile.update({
                'lsa_send_interval': 10.0,
                'heartbeat_interval': 1.2,
                'heartbeat_timeout_threshold': 10,
                'failure_detection_silence_seconds': 20.0,
                'spf_min_interval': 1.0,
                'log_level': logging.WARNING,
            })

        return profile
    
    def load_config(self) -> bool:
        """加载网络拓扑配置"""
        try:
            config_path = Path(self.config_file)
            if not config_path.exists():
                self.logger.error(f"配置文件不存在: {self.config_file}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.config = config
            self.logger.info(f"成功加载配置文件: {self.config_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            return False
    
    def build_network(self) -> bool:
        """构建网络拓扑"""
        try:
            # 导入Router类
            from src.core.router import Router
            router_port_map = {}
            router_count = len(self.config.get('routers', []))
            runtime_profile = self._get_runtime_profile(router_count)
            
            # 创建路由器实例
            for router_config in self.config.get('routers', []):
                router_id = router_config['router_id']
                router_name = router_config['router_name']
                listen_port = router_config['listen_port']
                listen_ip = router_config.get('listen_ip', '127.0.0.1')
                
                router = Router(router_id, router_name, listen_port, listen_ip)
                router.apply_runtime_profile(**runtime_profile)
                self.routers[router_id] = router
                router_port_map[router_id] = listen_port
                self.logger.info(f"创建路由器: {router_name} (ID={router_id})")
            
            # 配置链路
            for link_config in self.config.get('links', []):
                router1_id = link_config['router1_id']
                router2_id = link_config['router2_id']
                cost = link_config.get('cost', 1)
                
                if router1_id in self.routers and router2_id in self.routers:
                    router1 = self.routers[router1_id]
                    router2 = self.routers[router2_id]
                    
                    # 添加邻接关系（双向）
                    router1.add_neighbor(router2_id, '127.0.0.1', router_port_map[router2_id], cost)
                    router2.add_neighbor(router1_id, '127.0.0.1', router_port_map[router1_id], cost)
                    
                    self.logger.info(f"配置链路: {router1_id} <-> {router2_id}, 成本={cost}")
            
            self.logger.info(f"网络拓扑构建完成，共{len(self.routers)}个路由器")
            if router_count >= 50:
                self.logger.warning(
                    "已启用50节点稳态参数: 心跳容忍提升、LSA降频、日志降级、故障检测静默期"
                )
            return True
        
        except Exception as e:
            self.logger.error(f"构建网络拓扑失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def add_router_dynamic(self, router_id: int, listen_port: int, router_name: str = None) -> bool:
        """运行中动态添加路由器。"""
        try:
            if router_id in self.routers:
                self.logger.warning(f"路由器 {router_id} 已存在")
                return False

            from src.core.router import Router
            router_name = router_name or f"Router{router_id}"
            router = Router(router_id, router_name, listen_port, '127.0.0.1')
            self.routers[router_id] = router

            if self.running:
                router.start()

            self.logger.info(f"动态添加路由器: {router_name} (ID={router_id}, 端口={listen_port})")
            return True
        except Exception as e:
            self.logger.error(f"动态添加路由器失败: {e}")
            return False

    def add_link_dynamic(self, router1_id: int, router2_id: int, cost: int = 1) -> bool:
        """运行中动态添加双向链路。"""
        try:
            if router1_id not in self.routers or router2_id not in self.routers:
                self.logger.error("动态添加链路失败: 路由器不存在")
                return False

            router1 = self.routers[router1_id]
            router2 = self.routers[router2_id]

            router1.add_neighbor(router2_id, router2.listen_ip, router2.listen_port, cost)
            router2.add_neighbor(router1_id, router1.listen_ip, router1.listen_port, cost)

            if self.running:
                router1._send_lsa()
                router2._send_lsa()

            self.logger.info(f"动态添加链路: {router1_id} <-> {router2_id}, 成本={cost}")
            return True
        except Exception as e:
            self.logger.error(f"动态添加链路失败: {e}")
            return False
    
    def start_simulation(self, wait_sync_seconds: float = 2.0) -> bool:
        """启动仿真"""
        try:
            self.logger.info("启动路由仿真系统...")
            
            # 启动所有路由器
            for router_id, router in self.routers.items():
                router.start()
                self.logger.info(f"路由器 {router_id} 已启动")
            
            self.running = True
            self.logger.info("仿真系统已启动")
            
            # 等待拓扑同步（UI模式使用较短等待，避免启动阶段假死感）
            if wait_sync_seconds > 0:
                self.logger.info(f"等待LSA同步 {wait_sync_seconds:.1f}s...")
                deadline = time.time() + wait_sync_seconds
                while self.running and time.time() < deadline:
                    time.sleep(0.1)
            
            return True
        
        except Exception as e:
            self.logger.error(f"启动仿真失败: {e}")
            return False
    
    def stop_simulation(self):
        """停止仿真"""
        self.logger.info("停止仿真系统...")
        
        for router_id, router in self.routers.items():
            try:
                router.stop()
                self.logger.info(f"路由器 {router_id} 已停止")
            except Exception as e:
                self.logger.error(f"停止路由器 {router_id} 失败: {e}")
        
        self.running = False
        self.logger.info("仿真系统已停止")
    
    def get_routing_table(self, router_id: int) -> Optional[Dict]:
        """获取指定路由器的路由表"""
        if router_id not in self.routers:
            return None
        
        router = self.routers[router_id]
        routes = router.routing_table.get_all_routes()
        
        result = {
            'router_id': router_id,
            'routes': {}
        }
        
        for dest, (next_hop, cost, path) in routes.items():
            result['routes'][dest] = {
                'next_hop': next_hop,
                'cost': cost,
                'path': ' -> '.join(map(str, path))
            }
        
        return result
    
    def get_topology(self, router_id: int = None) -> Dict:
        """获取网络拓扑信息"""
        if router_id and router_id in self.routers:
            return self.routers[router_id].get_topology_data()
        
        # 返回全局视图
        nodes = {}
        edges = set()
        
        for router in self.routers.values():
            topology_data = router.get_topology_data()
            for node in topology_data['nodes']:
                nodes[node['id']] = node
            for edge in topology_data['edges']:
                # 避免重复边
                edge_tuple = tuple(sorted([edge['source'], edge['target']]))
                edges.add((edge_tuple[0], edge_tuple[1], edge['cost']))
        
        return {
            'nodes': list(nodes.values()),
            'edges': [{'source': e[0], 'target': e[1], 'cost': e[2]} for e in edges]
        }
    
    def simulate_link_failure(self, router1_id: int, router2_id: int):
        """模拟链路故障"""
        if router1_id in self.routers and router2_id in self.routers:
            router1 = self.routers[router1_id]
            router2 = self.routers[router2_id]
            
            router1.remove_neighbor(router2_id)
            router2.remove_neighbor(router1_id)
            
            self.logger.warning(f"模拟链路故障: {router1_id} <-> {router2_id}")
    
    def simulate_link_recovery(self, router1_id: int, router2_id: int, cost: int = 1):
        """模拟链路恢复"""
        if router1_id in self.routers and router2_id in self.routers:
            router1 = self.routers[router1_id]
            router2 = self.routers[router2_id]
            
            router1.add_neighbor(router2_id, '127.0.0.1', 
                               self.routers[router2_id].listen_port, cost)
            router2.add_neighbor(router1_id, '127.0.0.1',
                               self.routers[router1_id].listen_port, cost)
            
            self.logger.warning(f"模拟链路恢复: {router1_id} <-> {router2_id}")

    def switch_topology_profile(self, config_file: str) -> bool:
        """切换拓扑配置并重新启动仿真。"""
        try:
            # 停止当前仿真
            if self.running:
                self.stop_simulation()

            # 清空旧路由器实例
            self.routers = {}
            self.config_file = config_file

            if not self.load_config():
                return False
            if not self.build_network():
                return False
            if not self.start_simulation():
                return False

            self.logger.info(f"已切换拓扑配置: {config_file}")
            return True
        except Exception as e:
            self.logger.error(f"切换拓扑失败: {e}")
            return False
    
    def print_summary(self):
        """打印仿真摘要"""
        print("\n" + "="*80)
        print("路由仿真系统摘要".center(80))
        print("="*80)
        
        for router_id, router in sorted(self.routers.items()):
            print(f"\n【 路由器 {router_id} 】")
            print(f"  名称: {router.router_name}")
            print(f"  监听地址: {router.listen_ip}:{router.listen_port}")
            print(f"  邻接路由器: {list(router._neighbors.keys())}")
            
            routing_table = router.routing_table.get_all_routes()
            if routing_table:
                print(f"  路由表:")
                for dest, (next_hop, cost, path) in sorted(routing_table.items()):
                    path_str = ' -> '.join(map(str, path))
                    print(f"    目标 {dest}: 下一跳={next_hop}, 成本={cost}, 路径={path_str}")
            else:
                print(f"  路由表: [空]")
        
        print("\n" + "="*80 + "\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='链路状态路由协议分布式仿真系统')
    parser.add_argument('--config', default='config/network_topology.json',
                       help='网络拓扑配置文件路径')
    parser.add_argument('--ui', action='store_true', help='启动UI界面')
    
    args = parser.parse_args()
    
    simulator = RoutingSimulator(args.config)
    
    # 加载配置
    if not simulator.load_config():
        return 1
    
    # 构建网络
    if not simulator.build_network():
        return 1
    
    # 如果要求启动UI
    if args.ui:
        try:
            from src.ui.main_window import MainWindow
            from PyQt5.QtWidgets import QApplication

            if not simulator.start_simulation(wait_sync_seconds=1.0):
                return 1
            
            app = QApplication(sys.argv)
            window = MainWindow(simulator)
            window.show()
            return app.exec_()
        except ImportError:
            logger.warning("无法导入PyQt5，将以命令行模式运行")
            args.ui = False
    
    # 启动仿真
    if not simulator.start_simulation(wait_sync_seconds=2.0):
        return 1
    
    try:
        # 打印摘要
        simulator.print_summary()
        
        if not args.ui:
            # 命令行模式：保持运行直到用户中断
            print("\n输入 'quit' 退出，'help' 查看命令列表")
            while True:
                try:
                    cmd = input("> ").strip().lower()
                    
                    if cmd == 'quit':
                        break
                    elif cmd == 'help':
                        print("可用命令:")
                        print("  summary        - 打印网络摘要")
                        print("  topology       - 打印网络拓扑")
                        print("  routes <id>    - 打印路由器<id>的路由表")
                        print("  fail <id1> <id2> - 模拟链路故障")
                        print("  recover <id1> <id2> <cost> - 模拟链路恢复")
                        print("  quit           - 退出程序")
                    elif cmd == 'summary':
                        simulator.print_summary()
                    elif cmd == 'topology':
                        import json
                        topology = simulator.get_topology()
                        print(json.dumps(topology, indent=2, ensure_ascii=False))
                    elif cmd.startswith('routes '):
                        router_id = int(cmd.split()[1])
                        routing_table = simulator.get_routing_table(router_id)
                        if routing_table:
                            import json
                            print(json.dumps(routing_table, indent=2, ensure_ascii=False))
                    elif cmd.startswith('fail '):
                        parts = cmd.split()
                        r1, r2 = int(parts[1]), int(parts[2])
                        simulator.simulate_link_failure(r1, r2)
                    elif cmd.startswith('recover '):
                        parts = cmd.split()
                        r1, r2 = int(parts[1]), int(parts[2])
                        cost = int(parts[3]) if len(parts) > 3 else 1
                        simulator.simulate_link_recovery(r1, r2, cost)
                    elif cmd:
                        print(f"未知命令: {cmd}")
                
                except Exception as e:
                    print(f"错误: {e}")
    
    finally:
        simulator.stop_simulation()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
