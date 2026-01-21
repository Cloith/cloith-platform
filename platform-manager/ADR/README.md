Architectural Decisions Record

🌐 Internal Networking & Portability Logic
The Challenge: Headless Container Networking
This project runs inside a VS Code DevContainer. Unlike a standard Virtual Machine, a container lacks a full init system (like systemd) and does not naturally possess a persistent network tunnel device (/dev/net/tun).

Architected Solution: Hermetic Tailscale Bootstrapping
To ensure the platform is portable and idempotent, we do not rely on the Host OS (Windows/macOS) for networking. Instead, the Platform Manager implements a "Self-Healing" networking layer within the container itself.

Key Design Decisions
1. Userspace Networking Mode (--tun=userspace-networking)
What it does: It tells Tailscale to run its own network stack entirely inside the application process rather than trying to create a virtual network card in the Linux Kernel.

Why: Traditional containers require the --privileged flag or NET_ADMIN capabilities to modify the host's network kernel. Userspace mode bypasses these requirements, allowing the platform to run on any restricted Docker/WSL2 host.

2. SOCKS5 Proxy (--socks5-server=localhost:1055)
What it does: Since userspace mode doesn't create a global network interface, local applications (like Ansible or the Manager) need a "gateway" to reach the Tailnet.

Why: This flag opens a doorway on port 1055. Any tool configured to use this SOCKS5 proxy can now "see" and communicate with other nodes (like your VPS) through the encrypted tunnel.

3. In-Memory State (--state=mem:)
What it does: Forces Tailscale to store its machine identity and session keys in RAM instead of writing a persistent file to /var/lib/tailscale.

Why: This ensures the container is Ephemeral. When the container stops, the "Identity" is wiped. This prevents the Tailscale Admin Console from being cluttered with "ghost" nodes from old container sessions and forces a clean authentication check via the Manager's Bitwarden integration every time.

4. Process Decoupling (subprocess.Popen)
What it does: The tailscaled engine is birthed as a detached background process group using os.setpgrp.

Why: This prevents the Python Manager from hanging while waiting for the daemon to finish. It ensures the network tunnel remains alive as a system service even after the specific Python script that started it has exited.

5. Manual Socket Provisioning
What it does: The script manually creates /var/run/tailscale/ before launch.

Why: The tailscale CLI communicates with the tailscaled daemon via a Unix Domain Socket (.sock). In a fresh container, this directory often doesn't exist, causing the CLI to fail with "communication" errors.

Lifecycle Flow
Directory Setup: Ensure the /var/run/tailscale path exists for the communication socket.

Engine Start: Launch the daemon in the background with Userspace, SOCKS5, and In-Memory flags.

Socket Validation: Poll the filesystem until the .sock file appears, confirming the engine is ready.

Authentication: Use tailscale up with a Pre-authorized Auth Key fetched from the Bitwarden Vault.