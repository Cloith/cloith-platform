import subprocess
import os
import time
import pexpect
import pexpect
from rich.console import Console

console = Console()

def network_check(session_key):
    # 1. Start the status spinner
    with console.status("[bold green]Starting Tailscale daemon...[/bold green]", spinner="dots"):
        
        # 2. Launch the process silently in the background
        subprocess.Popen(
            ["sudo", "tailscaled", "--tun=userspace-networking"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

        # 3. Stay inside the 'with' block while waiting for the socket
        # This keeps the animation running!
        socket_path = "/var/run/tailscale/tailscaled.sock"
        success = False
        
        for _ in range(15):  # Slightly longer timeout for safety
            if os.path.exists(socket_path):
                success = True
                break
            time.sleep(0.5) # Check every half second for better responsiveness

    # 4. Feedback after the spinner finishes
    if success:
        console.print("[green]✓ Tailscale daemon is live.[/green]")
    else:
        console.print("[red]× Failed to start Tailscale daemon (Socket timeout).[/red]")
    

    
