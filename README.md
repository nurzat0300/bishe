# 链路状态路由协议分布式仿真系统

## 项目简介
这是一个链路状态路由协议（OSPF/IS-IS风格）的分布式仿真系统，用于研究和验证路由算法。

## 主要功能
- 多路由器的分布式仿真
- LSA洪泛和拓扑同步
- Dijkstra和新型最短路径算法实现
- 节点故障检测与恢复
- 可视化UI界面显示网络拓扑和路由表

## 项目结构
```
├── src/                      # 源代码目录
│   ├── core/               # 核心路由协议实现
│   │   ├── router.py       # 路由器类
│   │   ├── lsa.py          # LSA数据结构和处理
│   │   ├── topology.py     # 拓扑管理
│   │   └── protocol.py     # 协议处理
│   ├── algorithms/         # 算法实现
│   │   ├── dijkstra.py     # Dijkstra算法
│   │   ├── new_algorithm.py # 新算法实现
│   │   └── path_calc.py    # 路径计算
│   ├── ui/                 # UI界面
│   │   ├── main_window.py  # 主窗口
│   │   ├── topology_view.py # 拓扑显示
│   │   └── styles.py       # 样式定义
│   └── simulator.py        # 仿真系统主程序
├── config/                 # 配置文件
│   └── network_topology.json # 网络拓扑配置
├── tests/                  # 测试文件
└── docs/                   # 文档
```

## 环境要求
- Python 3.8+
- PyQt5
- numpy

## 快速开始
```bash
pip install -r requirements.txt
python src/simulator.py
```

## Windows 一键启动（双击图标）

项目根目录已提供以下启动文件：

- `start_ui.bat`：可直接双击启动（会自动创建 `.venv`、安装依赖并启动 UI）
- `start_ui.vbs`：可直接双击启动（隐藏命令行窗口）

推荐首次双击 `start_ui.bat`，观察是否有依赖安装报错；后续可用 `start_ui.vbs` 无窗口启动。
如果双击 `start_ui.vbs` 没有弹出 UI，请查看 `logs/start_ui_last.log`，或先双击 `start_ui.bat` 查看实时错误信息。

## 功能模块说明

### 1. 路由器实例 (Router)
- 监听UDP消息
- 使用多线程处理各种任务
- 维护拓扑数据库（LSDB）
- 定时发送LSA和心跳消息

### 2. LSA处理 (LSA Protocol)
- 序列号管理和去重
- 可靠的洪泛机制
- 避免广播风暴

### 3. 拓扑同步 (Topology Synchronization)
- Dijkstra算法计算最短路径树
- 新算法集成与对比
- 实时拓扑更新

### 4. 故障处理 (Fault Detection)
- 心跳消息检测
- 邻居失效判定
- 自动恢复机制

### 5. UI界面
- 实时显示网络拓扑图
- 显示各路由器的路由表
- 支持手动添加/删除节点和链路
- 实时日志输出

## 开发进度
- [ ] 基础框架搭建
- [ ] UDP通信和路由器核心类
- [ ] LSA协议实现
- [ ] 算法实现
- [ ] 故障检测机制
- [ ] UI界面
- [ ] 系统测试
