"""
系统测试脚本
"""
import sys
import os
import time

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulator import RoutingSimulator


def test_basic_simulation():
    """测试基本仿真"""
    print("\n" + "="*80)
    print("测试1: 基本仿真功能".center(80))
    print("="*80 + "\n")
    
    simulator = RoutingSimulator('config/network_topology.json')
    
    # 加载配置
    if not simulator.load_config():
        print("❌ 加载配置失败")
        return False
    
    # 构建网络
    if not simulator.build_network():
        print("❌ 构建网络失败")
        return False
    
    # 启动仿真
    if not simulator.start_simulation():
        print("❌ 启动仿真失败")
        return False
    
    # 等待拓扑同步
    print("⏳ 等待拓扑同步（10秒）...")
    time.sleep(10)
    
    # 检查拓扑同步
    print("\n✓ 检查拓扑同步状态:")
    router1 = simulator.routers[1]
    all_nodes = router1.topology.get_all_routers()
    expected_nodes = {1, 2, 3, 4, 5}
    
    if set(all_nodes) == expected_nodes:
        print(f"  ✓ Router1 已同步所有节点: {sorted(all_nodes)}")
    else:
        print(f"  ✗ Router1 拓扑不完整。已知节点: {sorted(all_nodes)}")
    
    # 检查路由表
    print("\n✓ 检查路由表:")
    for router_id, router in sorted(simulator.routers.items()):
        routes = router.routing_table.get_all_routes()
        print(f"  Router{router_id}: {len(routes)} 条路由")
        if len(routes) < len(simulator.routers) - 1:
            print(f"    警告: 路由表项数不足（期望{len(simulator.routers)-1}）")
    
    # 打印摘要
    simulator.print_summary()
    
    # 停止仿真
    simulator.stop_simulation()
    
    print("✓ 基本仿真测试完成！\n")
    return True


def test_link_failure():
    """测试链路故障"""
    print("\n" + "="*80)
    print("测试2: 链路故障与恢复".center(80))
    print("="*80 + "\n")
    
    simulator = RoutingSimulator('config/test_topology2.json')
    
    if not simulator.load_config() or not simulator.build_network() or not simulator.start_simulation():
        print("❌ 初始化失败")
        return False
    
    print("⏳ 等待初始拓扑同步...")
    time.sleep(10)
    
    # 获取初始路由表
    router1 = simulator.routers[1]
    initial_routes = len(router1.routing_table.get_all_routes())
    print(f"\n初始状态: Router1 有 {initial_routes} 条路由")
    
    # 模拟故障
    print("\n模拟链路 1<->2 故障...")
    simulator.simulate_link_failure(1, 2)
    
    print("⏳ 等待重新收敛...")
    time.sleep(5)
    
    # 检查故障后的状态
    after_failure_routes = len(router1.routing_table.get_all_routes())
    print(f"故障后: Router1 有 {after_failure_routes} 条路由")
    
    # 模拟恢复
    print("\n模拟链路 1<->2 恢复...")
    simulator.simulate_link_recovery(1, 2, cost=7)
    
    print("⏳ 等待重新收敛...")
    time.sleep(5)
    
    # 检查恢复后的状态
    after_recovery_routes = len(router1.routing_table.get_all_routes())
    print(f"恢复后: Router1 有 {after_recovery_routes} 条路由")
    
    simulator.stop_simulation()
    
    if after_recovery_routes > after_failure_routes:
        print("\n✓ 链路故障与恢复测试成功！")
        return True
    else:
        print("\n✗ 链路故障与恢复测试失败！")
        return False


def test_algorithm_comparison():
    """测试算法对比"""
    print("\n" + "="*80)
    print("测试3: 多算法性能对比".center(80))
    print("="*80 + "\n")
    
    simulator = RoutingSimulator('config/test_topology2.json')
    
    if not simulator.load_config() or not simulator.build_network() or not simulator.start_simulation():
        print("❌ 初始化失败")
        return False
    
    print("⏳ 等待拓扑同步...")
    time.sleep(10)
    
    router1 = simulator.routers[1]
    
    print(f"\n对比算法性能（节点ID: {router1.router_id}）")
    print("="*60)
    
    # 执行多算法基准
    results = router1.path_calculator.benchmark_algorithms(runs=10)
    
    # 显示对比结果
    print(f"{'算法名称':<24} {'平均时间(ms)':<15} {'平均访问节点':<15} {'平均迭代':<15}")
    print("-" * 76)

    display_map = {
        'dijkstra': 'Dijkstra',
        'new_algo': '新型算法',
        'bellman_ford': 'Bellman-Ford',
        'spfa': 'SPFA',
        'prim_mst': 'Prim(MST基线)',
        'floyd_warshall': 'Floyd-Warshall',
        'astar': 'A*',
    }

    for key in ['dijkstra', 'new_algo', 'bellman_ford', 'spfa', 'prim_mst', 'floyd_warshall', 'astar']:
        stats = results.get(key)
        if not stats:
            continue
        print(f"{display_map.get(key, key):<24} "
              f"{stats.get('avg_time_ms', 0):<15.4f} "
              f"{stats.get('avg_visited_nodes', 0):<15.2f} "
              f"{stats.get('avg_iterations', 0):<15.2f}")
    
    simulator.stop_simulation()
    
    print("\n✓ 算法对比完成！\n")
    return True


def test_routing_tables():
    """测试路由表正确性"""
    print("\n" + "="*80)
    print("测试4: 路由表正确性验证".center(80))
    print("="*80 + "\n")
    
    simulator = RoutingSimulator('config/test_topology3.json')
    
    if not simulator.load_config() or not simulator.build_network() or not simulator.start_simulation():
        print("❌ 初始化失败")
        return False
    
    print("⏳ 等待拓扑同步...")
    time.sleep(10)
    
    # 验证所有路由器的路由表
    print("\n路由表验证结果:")
    print("="*60)
    
    all_correct = True
    for router_id, router in sorted(simulator.routers.items()):
        routes = router.routing_table.get_all_routes()
        
        # 检查路由到其他所有路由器
        expected_destinations = set(simulator.routers.keys()) - {router_id}
        actual_destinations = set(routes.keys())
        
        status = "✓" if expected_destinations == actual_destinations else "✗"
        print(f"\n{status} Router{router_id}:")
        print(f"  期望路由到: {sorted(expected_destinations)}")
        print(f"  实际路由到: {sorted(actual_destinations)}")
        
        if expected_destinations != actual_destinations:
            all_correct = False
            missing = expected_destinations - actual_destinations
            if missing:
                print(f"  缺少路由: {missing}")
        
        # 显示一些路由详情
        if len(routes) > 0:
            for dest, (next_hop, cost, path) in sorted(routes.items())[:3]:
                path_str = ' → '.join(map(str, path))
                print(f"    到 {dest}: 下一跳={next_hop}, 成本={cost}, 路径={path_str}")
            if len(routes) > 3:
                print(f"    ... 还有 {len(routes)-3} 条路由")
    
    simulator.stop_simulation()
    
    if all_correct:
        print("\n✓ 路由表验证完成！所有路由器的路由表都是完整的。\n")
    else:
        print("\n✗ 路由表验证发现问题！\n")
    
    return all_correct


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + "链路状态路由协议分布式仿真系统 - 测试套件".center(78) + "║")
    print("╚" + "="*78 + "╝")
    
    tests = [
        ("基本仿真", test_basic_simulation),
        ("链路故障与恢复", test_link_failure),
        ("算法性能对比", test_algorithm_comparison),
        ("路由表验证", test_routing_tables)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
        
        time.sleep(2)  # 测试间隔
    
    # 测试总结
    print("\n" + "="*80)
    print("测试总结".center(80))
    print("="*80 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
