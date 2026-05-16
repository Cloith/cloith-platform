# Platform Manager
> **Bridging the "Ops Gap": Professional-grade automation for secure, low-cost VPS orchestration.**

[![Security: Zero-Leak](https://img.shields.io/badge/Security-Zero--Leak-red.svg)](#security-philosophy)
[![Infrastructure: Agnostic](https://img.shields.io/badge/Infra-Agnostic-blue.svg)](#the-problem-the-ops-gap)
[![UI: Textual](https://img.shields.io/badge/UI-Textual-green.svg)](https://textual.textualize.io/)
## Development Environment (Dev Container)

This application is designed to run exclusively inside a **VS Code Dev Container**. 

## Why?
Because the platform manager coordinates infrastructure using multiple cloud and systems utilities, it enforces an "Environment as Code" model. The container automatically provisions, configures, and isolates all required CLI dependencies so you do not have to install them manually on your host machine.


### Included Toolchain Matrix
The Dev Container automatically installs and configures the following tools:

| Category | Tool | Purpose |
| :--- | :--- | :--- |
| **Infrastructure** | `Terraform` | Infrastructure as Code provisioning |
| **Configuration** | `Ansible` | Server hardening and system configurations |
| **Secrets** | `Bitwarden CLI (bw)` | Secure vault session management & token retrieval |
| **Networking** | `Tailscale` | Mesh VPN/Overlay network management |
| **Orchestration** | `Kubectl` / `Helm` / `Skaffold` | Kubernetes deployment pipelines |
| **Testing & UI** | `Pytest` / `Textual` | Testing framework and TUI engine |

### Current Limitations (Scope)
* **Solo-Developer / Single-Machine Scope:** The lock mechanism utilizes a local file path (`/tmp/platform_manager.lock`). Therefore, it only prevents concurrent execution *on the same machine*. 
* **Team Deployment Warning:** If multiple developers run this tool from different machines simultaneously against the same remote infrastructure, the local lock will not prevent overlapping changes.

## The Mission: Democratizing Secure Hosting
Modern developers face a "Time vs. Money" dilemma: pay a massive premium for managed cloud platforms (AWS/Heroku) or struggle with the manual security "hustle" of a raw VPS.

**Cloith Platform** makes the "cheap naked VPS" option a professional reality. By automating critical provisioning and "Zero-Leak" security steps, this tool allows developers to maintain full control of their hardware without sacrificing the operational convenience of a managed service.

### Prerequisites
Before launching the project, ensure your host machine has:
1. **Docker Desktop** (or Docker Engine with Compose)
2. **VS Code**
3. **Dev Containers Extension** (by Microsoft)

### Getting Started inside the Container
1. Clone the repository to your local machine.
2. Open the project folder in VS Code.
3. When prompted in the bottom-right corner, click **"Reopen in Container"** (or press `F1`, type `Dev Containers: Reopen in Container`).
4. Once the build finishes, your terminal will automatically be placed into the pre-configured virtual environment (`/home/vscode/venv`) with all tools ready.

### Built-in CLI Shortcuts
The container injects custom bash aliases to streamline development and debugging:

* `manager`: Instantly boots the Textual TUI platform application.
* `wmanager`: Launches the TUI with hot-reloading (automatically restarts when you edit `.py` or `.tcss` files).
* `nuke-manager`: Cleanly terminates frozen application processes, kills stale Bitwarden CLI sessions, and purges the `/tmp/manager.lock` file.
