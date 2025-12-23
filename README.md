![Status](https://img.shields.io/badge/Status-Active%20Development-green)
# Cloud-Native Real-Time Event Platform

# 📖 The Project
Project Cloith is a Cloud-Native real-time platform designed to showcase highly available, containerized infrastructure. By leveraging Microservices architecture and Kubernetes orchestration, the platform facilitates sub-second latency event streaming between a Node.js backend and a React frontend via an MQTT-over-WebSockets bridge.

# 🛠️ Tech Stack

<img width="328" height="213" alt="image" src="https://github.com/user-attachments/assets/6783848e-888a-4056-b7d1-500ba0f70897" />

# 🚦 WebSocket Handshake Verification:

Manual Handshake Simulation
You can use powershell for this

Command 1 (windows power shell)1:
* $headers = @{"Connection"="Upgrade"; "Upgrade"="websocket"; "Sec-WebSocket-Key"="SGVsbG8sIHdvcmxkIQ=="; "Sec-WebSocket-Version"="13"}
* Invoke-WebRequest -Uri "http://srv1154036.hstgr.cloud/mqtt" -Headers $headers -Method Get -UseBasicParsing

Command 2 (curl):
* curl.exe -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
  -H "Sec-WebSocket-Version: 13" \
  http://srv1154036.hstgr.cloud/mqtt

Expected Output: StatusCode: 101 (Switching Protocols) This confirms the Gateway-to-Service bridge is functional and ready for real-time streams.

# 🚀 Roadmap
* [x] Establish K3s Cluster & NGINX Gateway Fabric

* [x] Implement WebSocket Protocol Switching via Gateway API

* [x] Connect Node.js Backend to MongoDB Atlas

* [ ] Infrastructure-as-Code (IaC): Provision server resources via Terraform.

* [ ] Observability: Deploy Prometheus/Grafana for real-time broker monitoring.
