from __future__ import annotations

import argparse
import sys
import threading
from pathlib import Path

from flask import Flask, jsonify, render_template

try:
    from scapy.all import IP, sniff
except ImportError:
    sniff = None
    IP = None

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from traffic_utils import TrafficStats, save_stats

app = Flask(__name__)
app.config['STATS_FILE'] = Path(__file__).resolve().parent / 'traffic_stats.json'

traffic_stats = TrafficStats()
traffic_lock = threading.Lock()
_capture_thread = None


def packet_callback(packet) -> None:
    if IP is None or sniff is None or IP not in packet:
        return

    with traffic_lock:
        traffic_stats.record(packet)


def start_sniffing(interface: str | None = None) -> None:
    global _capture_thread

    if sniff is None or IP is None:
        app.logger.warning('Scapy is not available. Install dependencies with pip install -r requirements.txt.')
        return

    if _capture_thread and _capture_thread.is_alive():
        return

    def _run_capture() -> None:
        try:
            sniff(filter='ip', prn=packet_callback, store=0, iface=interface)
        except PermissionError:
            app.logger.error('Permission denied while starting live capture. Try running with sudo.')
        finally:
            save_stats(str(app.config['STATS_FILE']), traffic_stats)

    _capture_thread = threading.Thread(target=_run_capture, daemon=True)
    _capture_thread.start()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stats')
def stats():
    return jsonify(traffic_stats.summary())


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'packet_count': traffic_stats.total_packets})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Run the Flask traffic dashboard.')
    parser.add_argument('-i', '--interface', default=None, help='Capture interface to use for live sniffing.')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Port for the Flask dashboard.')
    return parser


if __name__ == '__main__':
    args = build_parser().parse_args()
    start_sniffing(interface=args.interface)
    app.run(host='0.0.0.0', port=args.port, debug=True)
