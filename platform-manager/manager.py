
import subprocess
import sys
import os
import json
import signal
import pexpect
from rich.console import Console
import questionary
from providers.bitwarden.auth import login_to_bitwarden 
from providers.tailscale.tailscale import network_check
from core.template_scanner import scan_and_provision


console = Console()

# Define the timeout 
IDLE_TIMEOUT = 600 # 10 minutes



def handler(signum, frame):
    """This function runs when the alarm goes off."""
    raise TimeoutError

def main():
    # PRE-FLIGHT RESET
    with console.status("[bold green]Initializing secure environment...[/bold green]"):
        pexpect.run("bw logout")
        pexpect.run("sudo pkill tailscaled")

    console.rule("[bold blue]Cloith Platform Manager[/bold blue]")
    
    try:
        # 1. AUTHENTICATION (The Gatekeeper)
        session_key = login_to_bitwarden()

        if not session_key:
            sys.exit(1)

        # 2. SYNC TO ENSURE LATEST VAULT DATA
        with console.status("[bold yellow]Syncing Bitwarden vault...[/bold yellow]"):
            subprocess.run(["bw", "sync", "--session", session_key], check=True, capture_output=True)

        # 3. TAILSCALE NETWORK CHECK
        network_check(session_key)

        # 4. TEMPLATE SCANNING & PROVISIONING CHECK
        if not scan_and_provision(session_key):
            sys.exit(1)

                
        # 2. THE APPLICATION LOOP (The "Living" App)
        while True:
            # Show the menu and get the user's choice
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(IDLE_TIMEOUT)
            
            choice = questionary.select(
                "Main Menu - Select an Action:",
                choices=[
                    "🚀 Infrastructure (Terraform)",
                    "🛠️  Configuration (Ansible)",
                    "📦 Kubernetes (Skaffold)",
                    "🔑 View Session Info",
                    "❌ Exit Manager"
                ]
            ).ask()

            signal.alarm(0)  # Reset the alarm after user input

            if choice == "❌ Exit Manager" or choice is None:
                console.print("[yellow]Shutting down manager...[/yellow]")
                break  # This breaks the 'while' loop and hits 'finally'

            elif choice == "🚀 Infrastructure (Terraform)":
                # Call your terraform function here
                # run_terraform(session_key)
                input("\nPress Enter to return to menu...") # Keeps output on screen

            elif choice == "🔑 View Session Info":
                console.print(f"Current Session: [cyan]{session_key[:12]}***[/cyan]")
                input("\nPress Enter to return to menu...")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Force shutdown (Ctrl+C).[/yellow]")
    except TimeoutError:
        console.print("\n[red]⏰ Session timed out due to inactivity.[/red]")

    finally:
        # this make sures to reset everything after you close the app
        with console.status("[bold yellow]Logging out of Tailscale...[/bold yellow]"):
            pexpect.run("sudo tailscale logout")
        with console.status("[bold yellow]🔥 Burning the bridge (Shutting down Tailscale)...[/bold yellow]"):
            pexpect.run("sudo pkill tailscaled")
        console.print("[green]✓ Tunnel destroyed. Attack surface minimized.[/green]")
        with console.status("[bold yellow]Logging out of bitwarden...[/bold yellow]"):
            pexpect.run("bw logout")
        console.print("[bold red]🔒 Session terminated. Goodbye![/bold red]")

if __name__ == "__main__":
    main()