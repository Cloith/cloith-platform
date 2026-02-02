# Platform Manager: Backend Architecture

## The Challenge: Orchestrating Unreliable External States
The primary role of the Platform Manager is to act as a Controller. It must coordinate between a local secret vault (Bitwarden), a networking engine (Tailscale), and configuration management (Ansible). The challenge lies in the fact that any of these external systems can fail, time out, or provide invalid data at any moment.

## Key Design Decisions
### 1. The Interrogation Engine (Pexpect Logic)
The Choice: Replacing standard subprocess calls with an interactive Pexpect stream.

The Reason: Most CLI tools are designed for humans, not scripts. Well-designed CLI tools print errors to stderr, while some poorly designed tools may mix output streams, but don't always return useful exit codes. By using pexpect, the backend "interrogates" the process. It watches the buffer for specific strings like "invalid key" or "backend error". This allows the backend to make intelligent decisions—like triggering a re-authentication loop—rather than simply crashing.

### 2. State-Driven Validation Loops
The Choice: Implementing a while not connected state-aware loop for network authentication.

The Reason: To ensure the system is Self-Healing, the backend doesn't just "try once." It maintains a state machine. If the validation check fails, the backend transitions to a "Correction State" (prompting for a new key), updates the global state (Bitwarden), and then rolls back to the "Authentication State." This ensures the script only proceeds once a "Verified Healthy" state is achieved.

### 3. Asynchronous Process Decoupling
The Choice: Using subprocess.Popen with start_new_session=True.

The Reason: In a micro-services mindset, the "Networking" service should outlive the "Orchestration" task. By birthing the tailscaled daemon in a new session group, the backend prevents Zombie Processes and ensures the network tunnel remains persistent. The Manager can exit cleanly while the infrastructure it created stays online.

## Technical Stack & Implementation
Logic Core: Python 3.10.12

Process Management: Pexpect (Interactive), Subprocess (Declarative)

Security Integration: Bitwarden CLI via Shell-wrapper

Concurrency: Non-blocking I/O for socket polling (/var/run/tailscale/)

## Trade-offs & Logic Constraints
| **Pros (The Wins)** | **Cons (The Constraints)** |
| :-- | :-- |
| Defensive Execution: The pexpect loop catches "Soft Failures" (like expired keys) that standard scripts would miss. | Complexity Overhead: The codebase is larger and more complex than a simple Shell script. |
| State Integrity: The Manager will not attempt to run Ansible playbooks unless the network state is verified as Connected. | Timing Sensitivity: The backend relies on polling loops and timeouts, which may need tuning for slower hardware. |
| Error Interrogation & Translation: Instead of passing through raw, cryptic stderr from external binaries, the Manager parses process streams in real-time. It translates low-level failures (like socket timeouts or auth-key expirations) into actionable, high-fidelity feedback for the user via the Rich interface. | Dependency Heavy: The backend requires specific Python libraries and the Bitwarden CLI to be pre-installed in the container. |