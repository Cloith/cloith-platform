import os
import socket

def audit_isolation():
    print("--- 🛡️ Starting Container Isolation Audit ---")
    
    # 1. Check for Volume Mounts (The Bridge)
    # We look for common host paths to see if they are visible
    suspicious_paths = ['/mnt/c', '/Users', '/home/host_user', '/root/.ssh']
    for path in suspicious_paths:
        if os.path.exists(path):
            print(f"⚠️  VULNERABILITY: Host path found at {path}")
        else:
            print(f"✅ CLEAN: {path} is not visible.")

    # 2. Check for "Privileged" Mode
    # If the container can see the host's raw disk devices, it's privileged.
    if os.path.exists('/dev/sda') or os.path.exists('/dev/nvme0n1'):
        print("⚠️  VULNERABILITY: Container might be PRIVILEGED. Host disks are visible.")
    else:
        print("✅ CLEAN: No direct host disk access detected.")

    # 3. Check for Network Gateway
    # Can we see the host's internal IP?
    try:
        host_ip = socket.gethostbyname('host.docker.internal')
        print(f"ℹ️  INFO: Host IP is reachable at {host_ip} (Standard Docker behavior)")
    except socket.gaierror:
        print("✅ CLEAN: Host network is fully isolated.")

if __name__ == "__main__":
    audit_isolation()