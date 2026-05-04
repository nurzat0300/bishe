"""
LSA数据包和洪泛管理
"""
import struct
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple
from enum import IntEnum
from datetime import datetime
from .constants import Link, LinkState

class LSAType(IntEnum):
    """LSA类型"""
    ROUTER_LSA = 1
    NETWORK_LSA = 2

@dataclass
class RouterLSA:
    """路由器LSA"""
    router_id: int
    sequence_number: int = 0
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    links: List[Link] = field(default_factory=list)
    
    def to_bytes(self) -> bytes:
        """序列化为字节"""
        links_data = []
        for link in self.links:
            links_data.append({
                'dest_id': link.dest_id,
                'cost': link.cost,
                'state': int(link.state)
            })
        
        data = {
            'router_id': self.router_id,
            'sequence_number': self.sequence_number,
            'timestamp': self.timestamp,
            'lsa_type': int(LSAType.ROUTER_LSA),
            'links': links_data
        }
        
        return json.dumps(data).encode('utf-8')
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'RouterLSA':
        """从字节反序列化"""
        json_data = json.loads(data.decode('utf-8'))
        links = [
            Link(
                dest_id=link['dest_id'],
                cost=link['cost'],
                state=LinkState(link['state'])
            )
            for link in json_data['links']
        ]
        
        return cls(
            router_id=json_data['router_id'],
            sequence_number=json_data['sequence_number'],
            timestamp=json_data['timestamp'],
            links=links
        )

@dataclass
class LSAPacket:
    """LSA包装（用于网络传输）"""
    packet_type: int = 3  # MESSAGE_TYPE.LSA
    source_router_id: int = 0
    sequence_number: int = 0
    lsa_data: RouterLSA = field(default_factory=lambda: RouterLSA(0))
    hop_count: int = 30  # TTL
    
    def to_bytes(self) -> bytes:
        """序列化为字节"""
        lsa_bytes = self.lsa_data.to_bytes()
        # 头部使用1字节消息类型，便于接收端按data[0]快速分发
        header = struct.pack(
            '!BIIB',
            int(self.packet_type),
            self.source_router_id,
            self.sequence_number,
            self.hop_count,
        )
        return header + lsa_bytes
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'LSAPacket':
        """从字节反序列化"""
        header_size = 10
        header = struct.unpack('!BIIB', data[:header_size])
        lsa_data = RouterLSA.from_bytes(data[header_size:])
        
        return cls(
            packet_type=header[0],
            source_router_id=header[1],
            sequence_number=header[2],
            hop_count=header[3],
            lsa_data=lsa_data
        )

class LSADatabase:
    """LSA数据库 - 用于去重和版本控制"""
    
    def __init__(self):
        # {source_router_id: (sequence_number, timestamp, lsa_data)}
        self._lsas: Dict[int, Tuple[int, float, RouterLSA]] = {}
    
    def is_new_lsa(self, source_id: int, seq_num: int) -> bool:
        """判断是否为新的LSA"""
        if source_id not in self._lsas:
            return True
        
        current_seq = self._lsas[source_id][0]
        # 序列号大于当前版本，则为新LSA
        return seq_num > current_seq
    
    def update_lsa(self, source_id: int, lsa: RouterLSA):
        """更新LSA"""
        self._lsas[source_id] = (lsa.sequence_number, lsa.timestamp, lsa)
    
    def get_lsa(self, source_id: int) -> RouterLSA:
        """获取指定的LSA"""
        if source_id in self._lsas:
            return self._lsas[source_id][2]
        return None
    
    def get_all_lsas(self) -> Dict[int, RouterLSA]:
        """获取所有LSA"""
        return {router_id: lsa_data[2] for router_id, lsa_data in self._lsas.items()}
    
    def clear(self):
        """清空数据库"""
        self._lsas.clear()
