# System Architecture: Platform Manager

This document outlines the design patterns and structural decisions governing the Platform Manager. The architecture is designed to be **modular**, **stateless**, and **secure-by-default**.

---

## 1. Core Design Patterns

### 🏗 The Service Factory Pattern
The heart of the application is a **Service Factory** located in the `services/` directory. This pattern decouples the core UI logic from specific infrastructure providers.

*   **Decoupling:** The main application does not need to know the implementation details of Hostinger, Tailscale, or Bitwarden. It simply requests a service by type.
*   **Extensibility:** Adding a new provider (e.g., AWS or GCP) only requires adding a new class that inherits from a `BaseProvider` without modifying the core orchestrator.
*   **Consistency:** Every service is instantiated with a unified interface, ensuring predictable behavior across the entire platform.

### 🔒 Single-Instance Enforcement (Singleton)
To prevent resource conflicts and database corruption (especially when handling encrypted vaults), the platform implements a strict **OS-level lock** mechanism.

*   **Lock Mechanism:** Uses `fcntl` to create an exclusive, non-blocking lock on `/tmp/platform_manager.lock`.
*   **Stale Lock Detection:** The system automatically detects if a previous instance crashed (stale PID) and cleans up the lock file to allow a fresh start.
*   **Safety:** This ensures that two instances don't try to access the Bitwarden CLI or modify the same k3s cluster simultaneously.

---

## 2. Service Directory Structure
The platform is organized into specialized service domains:

| Directory | Purpose | Key Example |
| :--- | :--- | :--- |
| `services/vaults/` | Handles secret management and credential retrieval. | `BitwardenTokenService` |
| `services/providers/` | Interfaces with external infrastructure APIs. | `HostingerProvider` |
| `services/network/` | Manages the overlay mesh network transport layer. | `TailscaleClient` |

---

## 3. The "Brain vs. Muscle" Philosophy
The architecture is split into two distinct execution zones to maintain a **Zero-Leak** security posture:

1.  **The Brain (Local):** The Python orchestrator lives in a hardware-isolated DevContainer on your local machine. It holds the "intent" and handles authentication with Bitwarden.
2.  **The Muscle (Remote Agent):** (Planned) Minimalist execution scripts that receive signed instructions from the Brain via the Tailscale mesh to perform local provisioning tasks on the target VPS.

---

## 4. Implementation Details: Instance Locking
```python
# snippet of the locking logic used in PlatformManager
def acquire():
    """Ensures only one instance runs, with stale lock detection."""
    # Uses fcntl.flock for atomic OS-level locking
    # Validates existing PIDs to prevent orphaned locks
```
## 5. The Provider Interface (The "Contract")
To ensure UI stability across the Textual dashboard, all services must inherit from a common base class. This prevents "Runtime AttributeErrors" when the UI switches between different infrastructure providers.

### Abstract Base Methods
The `BaseProvider` defines the minimum required methods that every provider MUST implement:

*   **`fetch_vps()`**: Returns a standardized list of active instances.
*   **`provision_node()`**: Triggers the initial setup logic.
*   **`get_status()`**: Returns health metrics for the specific provider.

### Benefits of the Base Interface
*   **Screen Agnosticism**: Textual screens interact with the `BaseProvider` type, not specific implementations.
*   **Safe Defaults**: The base class provides default error handling and logging, so individual providers only need to focus on their unique API logic.
*   **Type Safety**: Utilizing Python type hints (e.g., `def get_provider(type) -> BaseProvider`) ensures the IDE and developer know exactly what methods are available.