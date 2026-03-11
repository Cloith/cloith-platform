#### [🏠 Home](../README.md) 
---
# Platform Manager

A secure infrastructure bootstrap and deployment manager for single-node VPS environments, designed around a stateless and ephemeral execution model. The tool acts as a portable gateway that orchestrates VPS provisioning, OS hardening, and containerized workload deployment (Docker or k3s) while dynamically fetching secrets from Bitwarden into volatile memory to ensure zero-persistence security.

It automates secure server initialization, configures ingress routing, and provides operational visibility through a Textual-based terminal UI. The system emphasizes reproducibility, secure defaults, and minimal manual configuration, enabling streamlined and security-focused small-scale infrastructure deployments.

![Platform Manager Demo](../platform-manager/docs/screenshots/demo.gif)

## Quick Start
[View the Step-by-Step Tutorial](../platform-manager/docs/TUTORIAL.md)

---

## Technical Architecture
I have documented the specific engineering domains applied in this project. Click a category to see the implementation details:

### [Networking](../platform-manager/docs/NETWORKING.md)
| Implementation Details |
| :--- |
| Userspace Tunneling |
| SOCKS5 Proxying |

### [Security](../platform-manager/docs/SECURITY.md)
| Implementation Details |
| :--- |
| Zero-Persistence Secrets |
| Bitwarden MFA Auth |

### [Linux Systems](../platform-manager/docs/LINUX.md)
| Implementation Details |
| :--- |
| Kernel Locking (`fcntl`) |
| FIFO Pipes (`mkfifo`) |

### [Backend Logic](../platform-manager/docs/BACKEND.md)
| Implementation Details |
| :--- |
| Pexpect State-Logic |
| Error Interrogation |

### [Frontend & UX](../platform-manager/docs/FRONTEND.md)
| Implementation Details |
| :--- |
| Interactive Prompts (Questionary) |
| Visual Status Feedback (Rich) |

---
#### [🏠 Home](../README.md) 