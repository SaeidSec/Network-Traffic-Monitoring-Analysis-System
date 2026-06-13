# Network Traffic Monitoring & Analysis System

A practical network monitoring and analysis project built in Python for packet capture, traffic inspection, metrics collection, and a simple Flask-based dashboard. The project combines:

- offline PCAP analysis,
- live packet capture and inspection,
- in-memory analytics and anomaly hints,
- a browser dashboard for quick visualization.

This repository is designed as a learning/demo platform and a starting point for building a more advanced traffic analysis system.

---

## 1. Executive Summary

This project is a compact traffic monitoring toolkit for capturing, inspecting, and summarizing network activity. It combines offline packet analysis, live interface capture, and a lightweight analytics dashboard. It is suitable for:

- learning packet analysis and Scapy workflows,
- prototyping network monitoring dashboards,
- evaluating traffic patterns in a test environment,
- building a base for a more advanced SIEM/monitoring platform.

The current implementation emphasizes readability and extensibility over deep production complexity. That makes it an ideal foundation for a student project, internal tool, or proof of concept.

---

## 2. Architecture Overview

The system is built around a simple pipeline:

1. Packet ingestion
   - Live traffic from a network interface
   - Offline traffic from a PCAP file
2. Packet normalization
   - Extract IPs, protocols, ports, and sizes
3. Metric aggregation
   - Count packets, bytes, top talkers, and protocol usage
4. Visualization / reporting
   - Display data in the Flask dashboard or save it to JSON

### Runtime flow

- `parse_pcap.py` reads saved capture files and prints summaries.
- `real_time_capture.py` captures packets from the active interface and displays them in real time.
- `real_time_analysis.py` applies threshold-based anomaly logic and reports suspicious activity.
- `traffic_utils.py` centralizes summary logic and persistence support.
- `web_interface/web_interface/app.py` serves the dashboard and statistics endpoint.

This separation keeps the logic reusable and makes it easier to extend the system later.

---

## 3. Deep Technical Breakdown

### 3.1 Packet parsing layer

The packet parsing path relies on Scapy to inspect every packet. The current parser focuses on:

- source and destination IP addresses,
- transport protocol,
- source and destination ports,
- packet length.

This is enough for basic traffic introspection, but it is intentionally limited. A production system would add:

- DNS, HTTP, TLS, and ICMP analysis,
- session reconstruction,
- flow-based grouping,
- protocol normalization,
- deep packet inspection.

### 3.2 Live traffic capture layer

The live capture tool listens to a network interface and processes packets as they arrive. It can be used for:

- monitoring a local host,
- observing traffic on a lab network,
- validating traffic flow in an internal environment,
- testing packet handling before moving to a larger system.

The current implementation is intentionally simple and is best used in controlled environments.

### 3.3 Analytics layer

The analytics layer maintains counters and summary statistics in memory while the tool runs. The current features include:

- packets per source IP,
- destination concentration,
- protocol distribution,
- port hit counts,
- average packet size,
- anomaly alerts for repeated traffic patterns.

This is a strong learning baseline but not a full detection engine.

### 3.4 Web/dashboard layer

The Flask front end provides a lightweight dashboard that reflects the current statistics. The UI polls the `/stats` endpoint periodically and renders summary tables in the browser.

This architecture is a good fit for:

- internal demos,
- debugging traffic capture logic,
- showing packet metrics to stakeholders,
- building a first prototype before adding charts and stored analytics.

---

## 4. Deployment Guide for a Professional Setup

The project can be deployed in a professional way in stages. The recommended setup depends on whether you want a local demo, a private internal service, or a production-grade monitoring platform.

### 4.1 Recommended environment

Use a Linux server or VM with:

- Python 3.10 or newer,
- a virtual environment,
- root or sudo access for live interface capture,
- network interface access for sniffing.

Suggested base stack:

- Ubuntu 22.04 LTS or Debian-based server
- Python 3.11
- Flask
- Scapy
- systemd for process management
- Nginx as a reverse proxy (optional but recommended)
- Gunicorn as the production WSGI server (recommended for Flask)

---

## 5. Professional Deployment Options

### Option A: Local development deployment

Good for testing and demos.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python web_interface/web_interface/app.py --port 5000
```

This is the fastest path for local use.

### Option B: Production-style Flask deployment

For a more professional deployment, use Gunicorn behind Nginx:

```bash
pip install gunicorn
```

Run the app with:

```bash
gunicorn --workers 2 --bind 0.0.0.0:8000 web_interface.web_interface.app:app
```

Then configure Nginx to proxy traffic to port 8000.

Example Nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.example;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

This setup is much more stable than using Flask’s built-in debug server in production.

### Option C: Systemd service deployment

To run the dashboard as a service on Linux:

1. Create a service file under /etc/systemd/system/network-traffic-dashboard.service
2. Configure the service to start Gunicorn
3. Enable and start it with systemctl

Example service:

```ini
[Unit]
Description=Network Traffic Dashboard
After=network.target

[Service]
User=your-user
WorkingDirectory=/home/your-user/Network-Traffic-Monitoring-Analysis-System
Environment="PATH=/home/your-user/Network-Traffic-Monitoring-Analysis-System/.venv/bin"
ExecStart=/home/your-user/Network-Traffic-Monitoring-Analysis-System/.venv/bin/gunicorn --workers 2 --bind 0.0.0.0:8000 web_interface.web_interface.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl daemon-reload
sudo systemctl enable network-traffic-dashboard
sudo systemctl start network-traffic-dashboard
```

This is the most professional way to run the dashboard on a real server.

---

## 6. Security and Operational Recommendations

If you deploy this for real use, follow these practices:

- do not expose the live capture interface to the public internet,
- run the dashboard behind authentication if it is used in a team environment,
- restrict network interface access to authorized users,
- use HTTPS in production,
- avoid storing sensitive traffic details in plain text unless necessary,
- log operational events and errors to a file,
- keep Python and Scapy updated.

For a more secure production environment, consider:

- auth-protected dashboard access,
- TLS certificates via Let’s Encrypt,
- rate limiting on the web endpoint,
- log rotation,
- a proper database backend for metrics.

---

## 7. Suggested Production Enhancements

To turn this prototype into a real professional monitoring system, consider these upgrades:

1. Move metrics storage from in-memory to PostgreSQL or SQLite.
2. Add charts for traffic trends over time.
3. Add authentication and role-based access.
4. Add filtering by protocol, host, port, and time range.
5. Support flow-based analytics instead of packet-level only.
6. Add alerting, notifications, and export features.
7. Improve anomaly detection with time-window heuristics and statistical baselines.
8. Add Docker support for portable deployment.

---

## 8. Docker Deployment Option

A professional deployment can also be containerized. A simple Docker setup would include:

- a Python image,
- the Flask dashboard,
- a mounted volume for logs and JSON artifacts,
- network privileges if live capture is required.

This makes the system easier to deploy across development, staging, and production environments.

---

## 9. Maintenance Checklist

For long-term use, keep the following in mind:

- update dependencies regularly,
- monitor CPU and memory usage,
- test the app after updates to Scapy or Flask,
- verify that live capture still works after system updates,
- rotate saved JSON outputs if the tool generates large files,
- document interface names and deployment assumptions clearly.

---

## 10. Summary

This repository is a solid starting point for a traffic monitoring project because it combines:

- practical packet analysis,
- live monitoring concepts,
- a web dashboard,
- useful metrics and persistence hooks.

It is not yet a full enterprise solution, but it is structured in a way that makes professional expansion realistic.

The system is organized into four main areas:

1. Packet parsing from saved PCAP files
2. Live network capture from a chosen interface
3. Traffic analysis and anomaly-style reporting
4. A lightweight Flask web dashboard for summary metrics

The goal is to help you investigate network traffic without relying on a heavy commercial stack.

---

## 2. Key Features

### Packet parsing
- Read existing PCAP files with Scapy
- Print per-packet summaries with source/destination, protocol, ports, and size
- Optionally export summaries to JSON

### Live capture
- Sniff traffic on a chosen interface
- Print live packet details in real time
- Save capture summaries to JSON files

### Traffic analysis
- Count total packets and bytes
- Track top source/destination IPs
- Count protocols and ports
- Calculate average packet length
- Highlight suspicious traffic using simple threshold-based logic

### Dashboard
- Show summary cards and tables in a browser
- Refresh traffic stats periodically
- Expose a simple health endpoint

---

## 3. Project Structure

```text
.
├── README.md
├── requirements.txt
├── capture.pcap
├── parse_pcap.py
├── real_time_capture.py
├── real_time_analysis.py
├── traffic_utils.py
├── tests/
│   └── test_traffic_utils.py
└── web_interface/
    └── web_interface/
        ├── app.py
        ├── static/
        │   └── style.css
        └── templates/
            └── index.html
```

### File descriptions

- README.md: Full project documentation.
- requirements.txt: Python dependencies for the project.
- capture.pcap: Sample PCAP file for testing the parser.
- parse_pcap.py: Offline PCAP parsing tool.
- real_time_capture.py: Live network capture tool.
- real_time_analysis.py: Traffic analysis and anomaly detection utility.
- traffic_utils.py: Shared metrics, summaries, and JSON persistence logic.
- tests/: Automated tests for the helper logic.
- web_interface/web_interface/app.py: Flask dashboard application.
- web_interface/web_interface/templates/index.html: Browser dashboard UI.
- web_interface/web_interface/static/style.css: Visual styling for the dashboard.

---

## 4. Requirements

The project depends on Python 3 and the following packages:

- Flask
- scapy

Install them with:

```bash
python -m pip install -r requirements.txt
```

If you are using the existing workspace virtual environment, the interpreter path is:

```bash
/home/saeidsec/Documents/Network Traffic Monitoring & Analysis System/.venv/bin/python
```

---

## 5. Getting Started

### 5.1 Clone or open the project

Open the workspace root and make sure you are in the project folder:

```bash
cd "/home/saeidsec/Documents/Network Traffic Monitoring & Analysis System"
```

### 5.2 Install dependencies

```bash
python -m pip install -r requirements.txt
```

If the environment already has a virtualenv configured, you can use the project venv directly:

```bash
"/home/saeidsec/Documents/Network Traffic Monitoring & Analysis System/.venv/bin/python" -m pip install -r requirements.txt
```

---

## 6. Usage Guide

### 6.1 Parse an existing PCAP file

Run the parser on the sample file:

```bash
python parse_pcap.py capture.pcap
```

To save the parsed result to JSON:

```bash
python parse_pcap.py capture.pcap --output parsed_packets.json
```

Example output:

```text
78:8c:b5:2b:a3:e8 -> c8:94:02:c1:50:a5 | TCP | ports 443:44960 | len=40
2e:a3:39:9b:9f:0d -> 01:00:5e:00:00:16 | 2 | ports *:* | len=40
```

This includes the source and destination addresses, the protocol, ports, and packet size.

### 6.2 Run live packet capture

Use a specific interface (for example, `eth0`, `wlan0`, or another available interface):

```bash
python real_time_capture.py --interface eth0
```

Useful options:

```bash
python real_time_capture.py --interface eth0 --count 100 --output capture_summary.json
```

- `--interface` chooses the network interface to monitor
- `--count` stops after N packets
- `--output` saves metrics to JSON
- `--threshold` tunes anomaly reporting

### 6.3 Run live traffic analysis

This script focuses more on traffic analysis and anomaly-style reporting:

```bash
python real_time_analysis.py --interface eth0
```

Useful options:

```bash
python real_time_analysis.py --interface eth0 --window 60 --threshold 20 --output analysis_summary.json
```

- `--window` sets the rolling time window for packet counting
- `--threshold` controls how many packets within the window are considered suspicious
- `--output` saves summary results to JSON

### 6.4 Start the Flask dashboard

Run the dashboard from the project root:

```bash
python web_interface/web_interface/app.py --port 5000
```

Then open:

```text
http://127.0.0.1:5000/
```

The dashboard shows:

- total packet count,
- total bytes,
- average packet size,
- anomaly count,
- top source IPs,
- top destination IPs,
- protocol counts,
- top ports.

---

## 7. How the Analytics Work

### Traffic metrics

The shared helper file `traffic_utils.py` collects:

- total_packets
- total_bytes
- top_sources
- top_destinations
- protocol_counts
- port_counts
- top_flows
- average_packet_length
- anomaly_sources

These values are stored in memory while the program runs and can also be saved to JSON.

### Anomaly-style reporting

The analysis logic uses simple heuristics:

- count packets from each source IP,
- monitor recent packet activity within a rolling time window,
- trigger warnings when the packet rate crosses a threshold.

This is intentionally simple and useful for demos, testing, and learning. It is not yet a full intrusion detection platform.

---

## 8. Testing

The repository includes automated tests for the core utility logic:

```bash
python -m unittest discover -s tests -v
```

These tests cover:

- packet summary extraction,
- traffic counting and anomaly hint behavior,
- JSON persistence and reload behavior.

---

## 9. Troubleshooting

### Permission issues on Linux

Live capture often requires elevated privileges. If you see a permission error, try:

```bash
sudo python real_time_capture.py --interface eth0
```

The web dashboard may also need elevated privileges depending on the environment and interface selection.

### Missing Scapy or Flask

If Python reports missing packages:

```bash
python -m pip install -r requirements.txt
```

### No output from the parser

Make sure the capture file exists and is readable:

```bash
ls -l capture.pcap
```

---

## 10. Current Limitations

This project is a prototype and currently has the following limitations:

- It is not a production-grade IDS/IPS system.
- Anomaly detection is heuristic-based rather than ML-driven.
- Traffic metrics are stored in memory while the app is running.
- Live capture depends on interface availability and system permissions.
- The dashboard is intentionally lightweight for learning and demonstration.

---

## 11. Possible Next Improvements

If you want to extend the project further, good next steps are:

1. Add charts and historical graphs.
2. Save statistics to a database instead of JSON.
3. Build better protocol and application-layer analysis.
4. Add filtering by IP, protocol, port, or timestamp.
5. Improve anomaly detection with more advanced rules.
6. Package the project for easier deployment.

---

## 12. License

This project is provided for educational and demonstration purposes. Review and follow the repository license file before using it in production or redistribution workflows.

