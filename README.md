![Status](https://img.shields.io/badge/Status-Active%20Development-green)

📖 New README Structure

🛰️ Project Cloith: Cloud-Native IaC & Event Platform

🏗️ Overview
Project Cloith is a self-orchestrating cloud infrastructure. Moving beyond manual configuration, the platform now features a Custom Python Orchestrator that manages secure deployments via Tailscale Zero-Trust tunnels, Bitwarden Secret injection, and Ansible.

The platform hosts a high-performance MQTT-over-WebSockets bridge, facilitating sub-second latency between a Node.js microservice backend and a React frontend.

🛠️ Infrastructure Orchestration (The "Manager")
The heart of this monorepo is the Platform Manager, a Python-based CLI tool designed for secure, idempotent environment management.

Key Engineering Features:

Zero-Trust Networking: Automatic Tailscale tunnel provisioning and teardown (Burning the Bridge policy).

Secure Secret Injection: Dynamic Bitwarden vault syncing; no secrets are ever stored on disk.

Singleton Execution: Implemented a system-level fcntl file lock to prevent race conditions during deployments.

Pre-Flight Sanitization: Automatic environment cleanup (purging sessions and pilling background daemons) before ogni run.

🚦 Technical Architecture
Current VPS Specs: 2 vCPU | 8GB RAM | K3s Cluster

System Flow:
Identity: Admin authenticates via the Manager using Bitwarden session keys.

Tunnel: Manager establishes an ephemeral Tailscale node for secure ingress.

Provision: Ansible templates are scanned, provisioned, and deployed to the K3s cluster.

Verification: The WebSocket Handshake (Status 101) confirms the Gateway-to-Service bridge.

🚀 Updated Roadmap
[x] Establish K3s Cluster & NGINX Gateway Fabric

[x] [New] Custom Python Platform Manager for automated orchestration.

[x] [New] Zero-Trust security integration via Tailscale.

[x] [New] Bitwarden CLI integration for secure secret management.

[ ] In Progress: CI/CD Quality Gates (Linter/Tester Pods) via GitHub Actions.

[ ] Planned: Real-time Chat App deployment within the secure mesh.
