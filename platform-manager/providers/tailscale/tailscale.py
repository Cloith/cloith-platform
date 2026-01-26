import subprocess
import os
import sys
import time
import pexpect
import questionary
from rich.console import Console
from providers.bitwarden.vault import get_secret
from providers.bitwarden.vault import update_key

console = Console()

def network_check(session_key):
    # 1. Start Daemon (Only needs to happen once)
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
    while not connected:
        auth_key = get_secret("tailscale_auth_key", session_key)

        child = pexpect.spawn(f"sudo tailscale up --auth-key={auth_key} --accept-routes --accept-dns=false", timeout=60, encoding='utf-8')
        with console.status("[bold yellow]Starting Tailscale net...[/bold yellow]") as status:    
            index = child.expect(["invalid key", "backend error", pexpect.EOF, pexpect.TIMEOUT])
        output = child.before if child.before else ""

        # Handle Late Arrivals on Timeout
        if index == 3:
            try: output += child.read_nonblocking(size=1000, timeout=1)
            except: pass

        # CHECK FOR FAILURE
        if index in [0, 1] or "invalid key" in output.lower():
            status.stop()
            console.print("[red]✘ Error: The Tailscale Auth Key is invalid.[/red]")
            
            if questionary.confirm("Would you like to update the key in your vault?").ask():
                new_key = questionary.password(
                    "Enter valid Tailscale Auth Key:",
                    validate=lambda text: True if text.strip() else "Must not be empty"
                ).ask()
                
                # if user cancels input while new_key is empty then it exits prevents uploading empty key
                if new_key is None:
                    sys.exit(1)
                with console.status("[bold yellow]Updating Tailscale Auth Key in vault...[/bold yellow]"):
                    update_key(new_key, session_key, name="tailscale_auth_key")
                continue # Retry connection with new key
            sys.exit(1)

        # CHECK FOR SUCCESS
        elif index == 2:
            if "error" in output.lower():
                console.print(f"[red]✘ Command failed:[/red] {output}")
                sys.exit(1)
            connected = True # Breaks the loop
            console.print("[green]✓ Tailscale connected successfully.[/green]")
    return True