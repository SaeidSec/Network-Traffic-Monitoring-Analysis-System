import json
import os
import tempfile
import unittest

from traffic_utils import TrafficStats, summarize_packet, save_stats, load_stats


class FakePacket:
    def __init__(self, src, dst, proto, sport=None, dport=None, length=60):
        self.src = src
        self.dst = dst
        self.proto = proto
        self.sport = sport
        self.dport = dport
        self.length = length


class TrafficUtilsTests(unittest.TestCase):
    def test_summarize_packet_extracts_basic_fields(self):
        packet = FakePacket('10.0.0.2', '10.0.0.3', 'TCP', 5000, 80, 120)

        summary = summarize_packet(packet)

        self.assertEqual(summary['src_ip'], '10.0.0.2')
        self.assertEqual(summary['dst_ip'], '10.0.0.3')
        self.assertEqual(summary['protocol'], 'TCP')
        self.assertEqual(summary['src_port'], 5000)
        self.assertEqual(summary['dst_port'], 80)
        self.assertEqual(summary['length'], 120)

    def test_traffic_stats_tracks_metrics_and_anomalies(self):
        stats = TrafficStats(window_seconds=60, anomaly_threshold=1.0)

        stats.record(FakePacket('10.0.0.2', '10.0.0.3', 'TCP', 5000, 80, 120), timestamp=0)
        stats.record(FakePacket('10.0.0.2', '10.0.0.4', 'TCP', 5001, 443, 110), timestamp=1)

        self.assertEqual(stats.total_packets, 2)
        self.assertEqual(stats.top_sources['10.0.0.2'], 2)
        self.assertEqual(stats.protocol_counts['TCP'], 2)
        self.assertEqual(stats.port_counts[80], 1)
        self.assertIn('10.0.0.2', stats.summary()['top_sources'])

    def test_persistence_round_trip(self):
        stats = TrafficStats()
        stats.record(FakePacket('10.0.0.2', '10.0.0.3', 'TCP', 5000, 80, 120))

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'traffic.json')
            save_stats(path, stats)
            loaded = load_stats(path)

            self.assertEqual(loaded['total_packets'], 1)
            self.assertIn('10.0.0.2', loaded['top_sources'])


if __name__ == '__main__':
    unittest.main()
