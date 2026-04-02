import subprocess
import os
import sys
import time
import pexpect
from rich.console import Console
from providers.bitwarden.vault import get_secret, update_key


console = Console()

def network_check(session_key):
    # 1. Start Daemon 
    with console.status("[bold green]Starting Tailscale daemon...[/bold green]"):
        subprocess.Popen(
            ["sudo", "tailscaled", "--tun=userspace-networking", "--socks5-server=localhost:1055"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True
        )

    # 2. Wait for socket
    socket_path = "/var/run/tailscale/tailscaled.sock"
    for _ in range(15):
        if os.path.exists(socket_path): break
        time.sleep(0.5)

    connected = False
    try:
        while not connected:
            auth_key = get_secret("tailscale_auth_key", session_key)
            
            targeted_env = {
                "TS_AUTHKEY": auth_key,
                "PATH": "/usr/sbin:/usr/bin:/sbin:/bin", 
                "TERM": os.environ.get("TERM", "xterm-256color")
            }

            cmd = "sudo -E tailscale up --authkey=$TS_AUTHKEY --accept-routes=false --accept-dns=false"

            child = pexpect.spawn(
                "sh", ["-c", cmd],
                env=targeted_env,
                timeout=60, 
                encoding='utf-8'
            )

            # --- SECURE REDACTION START ---
            targeted_env["TS_AUTHKEY"] = "0" * len(auth_key) 
            del targeted_env["TS_AUTHKEY"]
            auth_key = None 

            with console.status("[bold yellow]Starting Tailscale net...[/bold yellow]") as status:    
                index = child.expect(["invalid key", "backend error", pexpect.EOF, pexpect.TIMEOUT])
            output = child.before if child.before else ""

            # Handle Late Arrivals on Timeout
            if index == 3:
                try: output += child.read_nonblocking(size=1000, timeout=1)
                except: pass

            # CHECK FOR FAILURE
            if index < 2 or "invalid key" in output.lower():
                status.stop()
                console.print("[red]✘ Error: The Tailscale Auth Key is invalid.[/red]")
                console.print("Triggering update logic...")
                update_key("tailscale_auth_key", session_key)

            # CHECK FOR SUCCESS
            elif index == 2:
                if "error" in output.lower():
                    console.print(f"[red]✘ Command failed:[/red] {output}")
                    sys.exit(1)
                connected = True # Breaks the loop
                console.print("[green]✓ Tailscale connected successfully.[/green]")

    finally:
        # Extra safety check to prevent the Traceback if auth_key is already None
        if 'auth_key' in locals() and auth_key is not None:
            auth_key = None
        if 'targeted_env' in locals() and "TS_AUTHKEY" in targeted_env:
            del targeted_env["TS_AUTHKEY"]
    return True