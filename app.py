from flask import Flask, render_template, jsonify
from scapy.all import sniff, IP
from collections import defaultdict

app = Flask(__name__)

traffic_stats = defaultdict(int)

def packet_callback(packet):
    if IP in packet:
        src_ip = packet[IP].src
        traffic_stats[src_ip] += 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def stats():
    return jsonify(dict(traffic_stats))

def start_sniffing():
    sniff(filter="ip", prn=packet_callback, store=0)

if __name__ == "__main__":
    import threading
    threading.Thread(target=start_sniffing).start()
    app.run(host='0.0.0.0', port=5000)
