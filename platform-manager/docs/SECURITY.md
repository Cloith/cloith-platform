#### [🏠 Home](../../README.md) | [⬅️ Back](../README.md)
---
# Security Architecture & Secret Orchestration

## The Challenge: The "Leaky Disk" Problem
Traditional automation often relies on .env files or temporary plaintext files to pass secrets to tools like Ansible. This creates a massive security risk: if a system crashes or an attacker gains access, those secrets can be recovered from the disk or logs.

## Architected Solution: The "Root of Trust" Workflow
This project implements a Zero-Persistence strategy. Secrets are fetched from an encrypted vault and injected directly into process memory or ephemeral streams, ensuring that sensitive data never touches the persistent storage of the container or the host.

## Key Design Decisions
### 1. Bitwarden CLI as the "Root of Trust"
The Choice: Using the Bitwarden CLI (bw) as the primary vault.

The Reason: Instead of hardcoding API keys, the Manager requires a master session key to unlock the vault at runtime. This ensures that even if the entire source code is compromised, the infrastructure remains secure because the "keys to the kingdom" are stored in a professional-grade, encrypted vault outside of the repository.

### 2. Ephemeral Injection via FIFO Pipes
The Choice: Passing secret keys to Ansible via Named Pipes (FIFOs).

The Reason: A FIFO pipe is a kernel-managed buffer. When the Manager writes a secret to the pipe:

The data exists only in RAM.

The pipe is Blocking: it waits for the receiver (Ansible) to "listen."

The data is Consumed: once Ansible reads the key, the buffer is emptied. This eliminates the risk of "forgotten" temporary files sitting in /tmp.

### 3. Automatic Credential Rotation (Self-Healing)
The Choice: Implementing a pexpect validation loop for Tailscale Auth Keys.

The Reason: Credentials eventually expire. Instead of a hard failure, the Manager detects the "Invalid Key" signal from the system. It then triggers a sub-routine to prompt for a new key, updates the Bitwarden Vault programmatically, and resumes the task. This ensures the Chain of Trust is maintained even when secrets change.


## Trade-offs & Architecture Constraints

| **Pros (The Wins)** | **Cons (The Constraints)** |
| :-- | :-- |
| Zero-Disk Exposure: Secrets are never written to the SSD, neutralizing "Resting Data" attacks. | Session Dependency: If the Bitwarden session expires mid-run, the Manager loses its ability to fetch new secrets. |
| Centralized Control: All infrastructure keys (Tailscale, SSH, API) are managed in one encrypted vault. | Complexity: Implementing FIFO pipes and pexpect loops is significantly harder than using simple .env files. |
| Audit Ready: Using a CLI-based vault allows for logging who accessed what secret and when. | Manual Intervention: A human must still provide the initial "Master Key" to unlock the vault for the session. |

---
#### [🏠 Home](../../README.md) | [⬅️ Back](../README.md)