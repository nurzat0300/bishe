"""
网络拓扑可视化组件
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl
import networkx as nx

# 优先使用中文字体，避免中文字符警告
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False


class NetworkTopologyWidget(QWidget):
    """网络拓扑可视化窗口"""
    
    def __init__(self, simulator):
        super().__init__()
        self.simulator = simulator
        self._cached_pos = None
        self._cached_signature = None
        self.init_ui()

        # 答辩稳态模式：默认关闭自动刷新，仅手动刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_topology)
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新拓扑")
        refresh_btn.clicked.connect(self.refresh_topology)
        button_layout.addWidget(refresh_btn)
        
        layout_btn = QPushButton("调整布局")
        layout_btn.clicked.connect(self.adjust_layout)
        button_layout.addWidget(layout_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 创建Matplotlib图表
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # 信息标签
        self.info_label = QLabel("手动刷新模式：请点击“刷新拓扑”更新视图")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # 初始化绘制
        self.refresh_topology()
    
    def refresh_topology(self):
        """刷新拓扑图"""
        try:
            topology = self.simulator.get_topology()
            self.draw_topology(topology)
        except Exception as e:
            self.info_label.setText(f"错误: {e}")
    
    def draw_topology(self, topology_data):
        """绘制拓扑图"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            # 创建NetworkX图
            G = nx.Graph()
            
            nodes = topology_data['nodes']
            edges = topology_data['edges']
            
            # 添加节点
            for node in nodes:
                G.add_node(node['id'], label=node['label'])
            
            # 添加边和权重
            for edge in edges:
                source = edge['source']
                target = edge['target']
                cost = edge.get('cost', 1)
                G.add_edge(source, target, weight=cost)
            
            if len(G.nodes) == 0:
                ax.text(0.5, 0.5, '暂无拓扑数据', ha='center', va='center')
                self.canvas.draw()
                return

            node_count = len(G.nodes)
            edge_count = len(G.edges)
            is_large_topology = node_count >= 40 or edge_count >= 120

            current_signature = (
                tuple(sorted(G.nodes)),
                tuple(sorted((min(u, v), max(u, v), d.get('weight', 1)) for u, v, d in G.edges(data=True)))
            )

            # 仅在拓扑结构变化时重新计算布局，否则复用缓存
            if self._cached_pos is None or self._cached_signature != current_signature:
                if is_large_topology:
                    # 大拓扑使用更轻量布局，减少切换时卡顿
                    self._cached_pos = nx.circular_layout(G)
                else:
                    self._cached_pos = nx.spring_layout(G, k=1.8, iterations=20, seed=42)
                self._cached_signature = current_signature

            pos = self._cached_pos
            
            # 绘制边
            nx.draw_networkx_edges(
                G, pos,
                ax=ax,
                width=2,
                edge_color='#888888',
                alpha=0.6
            )
            
            # 绘制节点
            node_colors = ['#FF6B6B' if n == self.simulator.routers[next(iter(self.simulator.routers))].router_id 
                          else '#4ECDC4' 
                          for n in G.nodes]
            
            nx.draw_networkx_nodes(
                G, pos,
                ax=ax,
                node_color=node_colors,
                node_size=700 if is_large_topology else 1500,
                alpha=0.9
            )
            
            # 绘制标签
            labels = {node: f'R{node}' for node in G.nodes}
            nx.draw_networkx_labels(
                G, pos,
                ax=ax,
                labels=labels,
                font_size=8 if is_large_topology else 10,
                font_weight='bold',
                font_color='white'
            )

            # 大拓扑不绘制边权标签，减轻渲染压力
            if not is_large_topology:
                edge_labels = {(u, v): d['weight'] for u, v, d in G.edges(data=True)}
                nx.draw_networkx_edge_labels(
                    G, pos,
                    ax=ax,
                    edge_labels=edge_labels,
                    font_size=8,
                    font_color='#333333'
                )
            
            ax.set_title('网络拓扑图', fontsize=14, fontweight='bold')
            ax.axis('off')
            
            # 更新信息标签
            num_nodes = node_count
            num_edges = edge_count
            num_routers = len(self.simulator.routers)
            
            self.info_label.setText(
                f"拓扑信息: {num_routers}个路由器 | {num_nodes}个已知节点 | {num_edges}条链路"
            )
            
            self.canvas.draw()
        
        except Exception as e:
            ax.text(0.5, 0.5, f'绘制失败: {str(e)}', ha='center', va='center')
            self.canvas.draw()
    
    def adjust_layout(self):
        """调整图布局"""
        # 用户主动调整时强制重算布局
        self._cached_signature = None
        self._cached_pos = None
        self.refresh_topology()
