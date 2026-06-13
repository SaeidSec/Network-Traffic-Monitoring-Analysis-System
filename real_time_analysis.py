from scapy.all import sniff, IP
from collections import defaultdict

traffic_stats = defaultdict(int)
THRESHOLD = 100  # Example threshold for anomalies

def packet_callback(packet):
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        traffic_stats[src_ip] += 1

        print(f"IP Packet: {src_ip} -> {dst_ip}")

        if traffic_stats[src_ip] > THRESHOLD:
            print(f"Anomaly detected from IP: {src_ip}")

def main():
    sniff(filter="ip", prn=packet_callback, store=0)

if __name__ == "__main__":
    main()
