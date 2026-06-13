from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from scapy.all import IP, TCP, UDP
except ImportError:  # pragma: no cover - fallback for environments without Scapy
    IP = TCP = UDP = None


def _has_layer(packet: Any, layer: Any) -> bool:
    try:
        return layer is not None and layer in packet
    except TypeError:
        return False


def _packet_field(packet: Any, *names: str, default: Any = None) -> Any:
    for name in names:
        if hasattr(packet, name):
            return getattr(packet, name)

    if _has_layer(packet, IP):
        ip_layer = packet[IP]
        for name in names:
            if hasattr(ip_layer, name):
                return getattr(ip_layer, name)

    if _has_layer(packet, TCP):
        tcp_layer = packet[TCP]
        for name in names:
            if hasattr(tcp_layer, name):
                return getattr(tcp_layer, name)

    if _has_layer(packet, UDP):
        udp_layer = packet[UDP]
        for name in names:
            if hasattr(udp_layer, name):
                return getattr(udp_layer, name)

    return default


class TrafficStats:
    """Simple in-memory traffic analysis helper with metrics and persistence support."""

    def __init__(self, window_seconds: int = 60, anomaly_threshold: float = 100.0) -> None:
        self.window_seconds = window_seconds
        self.anomaly_threshold = anomaly_threshold
        self.total_packets = 0
        self.total_bytes = 0
        self.top_sources: Counter[str] = Counter()
        self.top_destinations: Counter[str] = Counter()
        self.protocol_counts: Counter[str] = Counter()
        self.port_counts: Counter[int] = Counter()
        self.flow_counts: Counter[str] = Counter()
        self.packet_lengths: list[int] = []
        self.last_anomalies: list[str] = []

    def record(self, packet: Any, timestamp: Optional[float] = None) -> None:
        src_ip = _packet_field(packet, 'src', default='unknown')
        dst_ip = _packet_field(packet, 'dst', default='unknown')

        protocol = _packet_field(packet, 'proto', default='IP')
        if protocol == 'IP' and _has_layer(packet, IP):
            protocol = 'IP'
        if _has_layer(packet, TCP):
            protocol = 'TCP'
        elif _has_layer(packet, UDP):
            protocol = 'UDP'

        src_port = _packet_field(packet, 'sport', default=None)
        dst_port = _packet_field(packet, 'dport', default=None)
        length = _packet_field(packet, 'len', 'length', default=0) or 0

        self.total_packets += 1
        self.total_bytes += length
        self.top_sources[src_ip] += 1
        self.top_destinations[dst_ip] += 1
        self.protocol_counts[protocol] += 1
        self.packet_lengths.append(length)

        if isinstance(src_port, int):
            self.port_counts[src_port] += 1
        if isinstance(dst_port, int):
            self.port_counts[dst_port] += 1

        flow_key = f"{src_ip}:{src_port or '*'}->{dst_ip}:{dst_port or '*'}"
        self.flow_counts[flow_key] += 1

        if self.top_sources[src_ip] >= self.anomaly_threshold:
            if src_ip not in self.last_anomalies:
                self.last_anomalies.append(src_ip)

    def summary(self) -> Dict[str, Any]:
        return {
            'total_packets': self.total_packets,
            'total_bytes': self.total_bytes,
            'top_sources': dict(self.top_sources.most_common(10)),
            'top_destinations': dict(self.top_destinations.most_common(10)),
            'protocol_counts': dict(self.protocol_counts),
            'port_counts': dict(self.port_counts.most_common(20)),
            'top_flows': dict(self.flow_counts.most_common(10)),
            'average_packet_length': round(sum(self.packet_lengths) / len(self.packet_lengths), 2) if self.packet_lengths else 0,
            'anomaly_sources': self.last_anomalies,
        }


def summarize_packet(packet: Any) -> Dict[str, Any]:
    src_ip = _packet_field(packet, 'src', default=None)
    dst_ip = _packet_field(packet, 'dst', default=None)
    protocol = _packet_field(packet, 'proto', default='IP')

    if protocol == 'IP' and _has_layer(packet, IP):
        protocol = 'IP'
    if _has_layer(packet, TCP):
        protocol = 'TCP'
    elif _has_layer(packet, UDP):
        protocol = 'UDP'

    return {
        'src_ip': src_ip,
        'dst_ip': dst_ip,
        'protocol': protocol,
        'src_port': _packet_field(packet, 'sport', default=None),
        'dst_port': _packet_field(packet, 'dport', default=None),
        'length': _packet_field(packet, 'len', 'length', default=0) or 0,
    }


def save_stats(path: str, stats: TrafficStats) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as handle:
        json.dump(stats.summary(), handle, indent=2)


def load_stats(path: str) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as handle:
        return json.load(handle)
