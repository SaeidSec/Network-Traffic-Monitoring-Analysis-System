from scapy.all import sniff, IP, TCP, UDP

def packet_callback(packet):
    if IP in packet:
        print(f"IP Packet: {packet[IP].src} -> {packet[IP].dst}")
        if TCP in packet:
            print(f"TCP Packet: {packet[TCP].sport} -> {packet[TCP].dport}")
        elif UDP in packet:
            print(f"UDP Packet: {packet[UDP].sport} -> {packet[UDP].dport}")
        else:
            print("Other IP Packet")

def main():
    sniff(filter="ip", prn=packet_callback, store=0)

if __name__ == "__main__":
    main()
