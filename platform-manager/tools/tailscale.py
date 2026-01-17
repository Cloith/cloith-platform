import subprocess
import os
import sys
import time
import pexpect

from rich.console import Console
from tools.vault import fetch_tailscale_auth

console = Console()

def network_check(session_key):
    
    with console.status("[bold green]Starting Tailscale daemon...[/bold green]") as status:
        subprocess.Popen(
            ["sudo", "tailscaled", "--tun=userspace-networking"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

    socket_path = "/var/run/tailscale/tailscaled.sock"
    success = False
    
    for _ in range(15):  # Slightly longer timeout for safety
        if os.path.exists(socket_path):
            success = True
            break
        time.sleep(0.5) # Check every half second for better responsiveness

        
    auth_key = fetch_tailscale_auth(session_key)
    if auth_key:
        with console.status("[bold green]Connecting to Tailscale net...[/bold green]"):
            
               
    
           
            # Authenticate with Tailscale using the retrieved key
           
            child = pexpect.spawn(f"sudo tailscale up --auth-key={auth_key} --accept-routes --accept-dns=false", timeout=30, encoding='utf-8')
            
            try:
                # We wait for Tailscale to either finish (EOF) or hit your specific error
                index = child.expect(["invalid key", pexpect.EOF])
                
                child.wait() 
                console.print(child.before)

                if index == 0:
                    console.print("[red]✘ Error:[/red] The Tailscale Auth Key in your vault is invalid.")
                    
                    sys.exit(1)

                    # child.wait() ensures the process is totally cleaned up
                    
                console.print(f"[green]✔ Tailscale connected successfully.[/green]")
                return True
            
                
                    

            except pexpect.TIMEOUT:
                console.print("[red]✘ Error:[/red] Tailscale connection timed out.")
                return False
        
    else:
        success = False
  
    if success:
        console.print("[green]✓ Tailscale daemon is live.[/green]")
    else:
        console.print("[red]× Failed to start Tailscale daemon (Socket timeout).[/red]")
    

    
