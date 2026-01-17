
from asyncio import subprocess
import sys
import os
import json
import signal
import pexpect
from rich.console import Console
import questionary
from auth import login_to_bitwarden 
from tools.tailscale import network_check


console = Console()

# Define the timeout 
IDLE_TIMEOUT = 600 # 10 minutes

STATE_FILE = "/workspaces/cloith-platform/platform-manager/.manager_state.json"

def load_manager_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"active_templates": []}

def save_manager_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

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
        state = load_manager_state()
        
        # 1. AUTHENTICATION (The Gatekeeper)
        session_key = login_to_bitwarden()
        if not session_key:
            sys.exit(1)

        

        # tailscale network check
        network_check(session_key)

        if state["active_templates"]:
            console.print(f"[green]Active Environment Detected:[/green] {state['active_templates']}")
        
        else:
            console.print("[yellow]No active environments found. Please select a template to begin.[/yellow]")
                

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