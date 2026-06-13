from scapy.all import rdpcap

def parse_pcap(file):
    packets = rdpcap(file)
    for packet in packets:
        print(packet.summary())  # For detailed inspection, use print(packet.show())

if __name__ == "__main__":
    pcap_file = "capture.pcap"
    parse_pcap(pcap_file)