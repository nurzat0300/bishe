"""
常量定义和配置
"""
import enum
from dataclasses import dataclass
from typing import List, Tuple

# 通信常量
UDP_BUFFER_SIZE = 4096
LSA_SEND_INTERVAL = 5  # 秒，LSA定时发送间隔
HEARTBEAT_INTERVAL = 0.8  # 秒，心跳发送间隔（降低高并发下CPU压力）
HEARTBEAT_TIMEOUT = 3  # 心跳超时次数，用于故障检测

# 消息类型
class MessageType(enum.IntEnum):
    HEARTBEAT = 1          # 心跳消息
    HELLO = 2              # HELLO消息（邻居发现）
    LSA = 3                # LSA数据包
    ACK = 4                # 确认消息

# 链路状态
class LinkState(enum.IntEnum):
    UP = 1                 # 链路正常
    DOWN = 0               # 链路故障

@dataclass
class RouterConfig:
    """路由器配置"""
    router_id: int
    router_name: str
    listen_port: int
    neighbors: List[Tuple[int, str, int]]  # [(neighbor_id, neighbor_ip, neighbor_port), ...]

@dataclass
class Link:
    """链路信息"""
    dest_id: int
    cost: int
    state: LinkState = LinkState.UP
    
@dataclass
class RouteEntry:
    """路由表项"""
    destination: int
    next_hop: int
    cost: int
    path: List[int]  # 完整路径

class Constants:
    """全局常量"""
    DEFAULT_LINK_COST = 1
    INFINITY = 65535
    MAX_ROUTERS = 255
