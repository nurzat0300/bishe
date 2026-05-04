# 使用说明

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 启动系统

### 方式一：命令行模式

```bash
python run.py
```

或指定配置文件：
```bash
python run.py --config config/test_topology2.json
```

### 方式二：图形界面模式

```bash
python run.py --ui
```

## 系统架构

### 核心模块

#### 1. `src/core/router.py` - 路由器实现
- 多线程UDP通信
- LSA处理和完整泛洪
- 心跳检测
- 拓扑数据库维护

#### 2. `src/core/lsa.py` - LSA协议
- LSA数据包定义
- 序列号管理和去重
- 可靠泛洪机制

#### 3. `src/core/topology.py` - 拓扑管理
- 网络拓扑图表示
- 路由表管理
- 邻接关系维护

#### 4. `src/core/protocol.py` - SPF计算
- 路径计算器
- 两种算法集成
- 统计数据收集

#### 5. `src/algorithms/` - 算法实现
- `dijkstra.py` - Dijkstra最短路径算法
- `new_algorithm.py` - 改进型算法（基于清华大学论文）

### UI模块

- `src/ui/main_window.py` - 主窗口和各个标签页
- `src/ui/topology_view.py` - 网络拓扑可视化
- `src/ui/styles.py` - 样式定义

## 配置文件格式

网络拓扑配置文件（JSON格式）：

```json
{
  "routers": [
    {
      "router_id": 1,
      "router_name": "Router1",
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

## 命令行命令

在命令行模式下，可用以下命令：

| 命令 | 说明 | 示例 |
|------|------|------|
| `summary` | 打印网络摘要 | `summary` |
| `topology` | 显示网络拓扑 | `topology` |
| `routes <id>` | 显示路由器路由表 | `routes 1` |
| `fail <id1> <id2>` | 模拟链路故障 | `fail 1 2` |
| `recover <id1> <id2> <cost>` | 恢复链路 | `recover 1 2 10` |
| `quit` | 退出程序 | `quit` |

## UI界面说明

### 1. 网络拓扑标签页
- 实时显示网络拓扑图
- 绿色节点代表已同步的路由器
- 红色边界代表本路由器视图
- 边上的数字表示链路成本

### 2. 路由表标签页
- 选择指定路由器查看其路由表
- 显示目标、下一跳、成本、完整路径
- 自动每2秒刷新

### 3. 算法对比标签页
- 选择源路由器执行两种算法对比
- 显示计算时间、访问节点数、迭代次数对比
- 帮助评估新算法的性能改进

### 4. 仿真控制标签页
- 模拟链路故障：选择两个路由器ID，创建故障
- 恢复链路：恢复故障链路并指定新的成本
- 实时显示系统统计信息

## 测试

运行系统测试：

```bash
python tests/run_tests.py
```

## 项目进度

完成情况：

- [x] 第1-2周: 需求分析和文献调研
- [x] 第3-5周: 系统框架和UDP通信
- [x] 第6-7周: LSA协议实现
- [x] 第8周: Dijkstra算法实现
- [x] 第9-10周: 新算法和故障处理
- [x] 第11-12周: UI和系统集成
- [ ] 第13周: 性能测试和对比
- [ ] 第14周: 论文编写

## 常见问题

### Q: 如何在不同的机器上运行？
A: 修改配置文件中的 `listen_ip` 为实际机器IP，并确保防火墙允许UDP通信。

### Q: 如何扩展到更多路由器？
A: 在配置文件中添加更多路由器定义和链路配置。建议最多50个路由器用于测试。

### Q: 如何修改心跳检测超时时间？
A: 修改 `src/core/constants.py` 中的 `HEARTBEAT_TIMEOUT` 常数。

### Q: 如何调整LSA发送间隔？
A: 修改 `src/core/constants.py` 中的 `LSA_SEND_INTERVAL` 常数。

## 相关论文和参考

- [1] Dijkstra, E. W. A note on two problems in connexion with graphs. 1959
- [2] RFC 2328 - OSPF Version 2
- [3] Kurose & Ross - Computer Networking (8th Edition)
- [4] 清华大学 - A Near-Optimal Algorithm for Shortest Paths in Weighted Graphs (2025)

## 许可证

本项目用于毕业设计研究，仅供学习使用。

## 联系方式

如有技术问题，请联系项目维护人员。
