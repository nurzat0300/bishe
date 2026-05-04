# 链路状态路由协议分布式仿真系统

## 项目简介
这是一个链路状态路由协议（OSPF/IS-IS风格）的分布式仿真系统，用于研究和验证路由算法。该系统完整实现了OSPF核心机制，包括邻接发现、LSA泛洪、拓扑同步和路径计算，支持Dijkstra和新型算法的对比测试，可以模拟网络故障和恢复。

## 主要功能
- ✓ 多路由器的分布式仿真（支持1-255个路由器）
- ✓ LSA洪泛和拓扑同步机制
- ✓ Dijkstra和新型最短路径算法实现
- ✓ 节点故障检测与恢复（心跳机制）
- ✓ 可视化UI界面显示网络拓扑和路由表
- ✓ 完整的路径显示和算法性能对比
- ✓ 支持链路故障和恢复模拟

## 系统特性

### 核心协议
- **邻接发现**：HELLO消息和心跳检测
- **可靠泛洪**：序列号管理，避免广播风暴
- **拓扑同步**：完整的LSDB维护
- **最短路径计算**：Dijkstra + 新算法
- **故障恢复**：0.3秒心跳间隔，3次超时判定故障

### 技术栈
- **后端**：Python 3.8+，多线程，UDP通信
- **前端**：PyQt5，matplotlib可视化
- **算法**：NetworkX（图论库）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动系统

**方式一：命令行模式**
```bash
python run.py
```

**方式二：图形界面模式**
```bash
python run.py --ui
```

**方式三：指定配置文件**
```bash
python run.py --config config/test_topology2.json --ui
```

### 3. 运行测试

```bash
python tests/run_tests.py
```

## 项目结构
```
├── src/                      # 源代码目录
│   ├── core/               # 核心路由协议实现
│   │   ├── router.py       # 路由器类（核心组件）
│   │   ├── lsa.py          # LSA数据结构和处理
│   │   ├── topology.py     # 拓扑管理（使用NetworkX）
│   │   ├── protocol.py     # SPF计算和路径计算
│   │   └── constants.py    # 常量定义
│   ├── algorithms/         # 算法实现
│   │   ├── dijkstra.py     # Dijkstra最短路径算法
│   │   └── new_algorithm.py # 新型最短路径算法
│   ├── ui/                 # UI界面
│   │   ├── main_window.py  # 主窗口和各标签页
│   │   ├── topology_view.py # 拓扑可视化
│   │   └── styles.py       # 样式定义
│   └── simulator.py        # 仿真系统主程序
├── config/                 # 配置文件
│   ├── network_topology.json    # 默认网络拓扑
│   ├── test_topology1.json      # 5节点测试拓扑
│   ├── test_topology2.json      # 10节点测试拓扑
│   └── test_topology3.json      # 环形拓扑
├── tests/                  # 测试文件
│   └── run_tests.py       # 完整的系统测试套件
├── docs/                   # 文档
│   ├── USAGE.md           # 使用说明
│   └── TECHNICAL.md       # 技术文档
├── requirements.txt        # 依赖列表
├── run.py                 # 启动脚本
└── README.md              # 本文件
```

## 使用说明

### 命令行模式命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `summary` | 打印网络摘要 | `summary` |
| `topology` | 显示网络拓扑JSON | `topology` |
| `routes <id>` | 显示路由器路由表 | `routes 1` |
| `fail <id1> <id2>` | 模拟链路故障 | `fail 1 2` |
| `recover <id1> <id2> <cost>` | 恢复链路 | `recover 1 2 10` |
| `help` | 显示帮助 | `help` |
| `quit` | 退出程序 | `quit` |

### UI界面说明

#### 1. 网络拓扑标签页
- 实时显示网络拓扑图
- 路由器位置自动布局
- 边上显示链路成本
- 自动每3秒刷新

#### 2. 路由表标签页
- 选择指定路由器查看其路由表
- 显示目标、下一跳、成本、完整路径
- 显示拓扑信息和LSA统计
- 自动每2秒刷新

#### 3. 算法对比标签页
- 选择源路由器执行两种算法
- 对比计算时间、访问节点数、迭代次数
- 帮助评估新算法性能

#### 4. 仿真控制标签页
- 模拟链路故障和恢复
- 实时显示系统运行统计
- 显示活跃邻接关系

## 配置文件格式

```json
{
  "routers": [
    {
      "router_id": 1,
      "router_name": "RouterA",
      "listen_port": 10001,
      "listen_ip": "127.0.0.1"
    }
  ],
  "links": [
    {
      "router1_id": 1,
      "router2_id": 2,
      "cost": 10
    }
  ]
}
```

## 核心算法说明

### 1. LSA洪泛机制
- **序列号管理**：自增序列号防止重复
- **TTL控制**：初始TTL=30，每转发递减1
- **去重处理**：维护最大序列号映射表

### 2. 心跳检测
- **发送间隔**：0.3秒
- **超时判定**：连续3次超时（>0.9秒）
- **故障处理**：自动生成新LSA，标记链路DOWN

### 3. SPF计算
- **Dijkstra**：标准实现，使用二叉堆优化
- **新算法**：分层优先队列，减少松弛操作
- **计算时机**：新LSA到达或拓扑变化时触发

## 系统性能指标

### 网络规模支持
- **最大节点数**：255（受byte限制）
- **推荐规模**：5-50节点（演示效果最佳）
- **最大测试规模**：100+节点

### 时间指标
- **拓扑同步时间**：~5-10秒（5节点网络）
- **故障检测时间**：~1秒
- **SPF计算时间**：<1ms（10节点）

## 测试覆盖

已实现的测试：
- [x] 基本仿真功能
- [x] 链路故障与恢复
- [x] 算法性能对比
- [x] 路由表正确性验证

运行测试：
```bash
python tests/run_tests.py
```

## 常见问题

**Q: 如何在多台机器上运行？**
A: 修改配置文件中的 `listen_ip` 为实际IP，确保防火墙允许UDP通信。

**Q: UI界面显示为空？**
A: 等待10秒让拓扑同步，或检查路由器是否正常启动。

**Q: 如何调整心跳超时？**
A: 修改 `src/core/constants.py` 中的 `HEARTBEAT_TIMEOUT`。

**Q: 新算法的具体实现原理？**
A: 详见 `src/algorithms/new_algorithm.py` 代码注释和 `docs/TECHNICAL.md`。

## 学习路线建议

1. **入门**：阅读README和使用说明，运行默认配置
2. **理解协议**：阅读 `router.py` 和 `lsa.py`
3. **研究算法**：查看 `dijkstra.py` 和 `new_algorithm.py`
4. **修改实验**：创建自定义拓扑，测试不同场景
5. **性能优化**：运行测试套件，对比算法性能

## 贡献指南

欢迎提交Bug报告和改进建议。主要改进方向：
- [ ] 支持更多路由协议（IS-IS等）
- [ ] 集成性能分析工具
- [ ] 支持分布式部署
- [ ] 增加动画演示功能

## 相关论文和参考

- [1] Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1(1), 269-271.
- [2] RFC 2328 - OSPF Version 2 (1998)
- [3] Kurose, J. F., & Ross, K. W. (2020). *Computer Networking* (8th ed.). Pearson.
- [4] 清华大学 (2025). A Near-Optimal Algorithm for Shortest Paths in Weighted Graphs.

## 许可证

本项目用于毕业设计研究，仅供学习使用。

## 致谢

感谢开源社区提供的优秀工具：PyQt5、NetworkX、Matplotlib等。
