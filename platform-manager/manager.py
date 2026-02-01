import os
import sys
import fcntl
import pexpect
import questionary
import subprocess
import socket
import threading
import termios
import time
import shutil
from rich.console import Console
from providers.bitwarden import login_to_bitwarden, sync_bitwarden_vault
from providers.tailscale.tailscale import network_check
from core.template_scanner import scan_and_provision
from core.deploy import deploy_template

console = Console()
internet_available = threading.Event()
connected = True
fd = sys.stdin.fileno()
attributes = termios.tcgetattr(fd)
internet_available.set()

IDLE_TIMEOUT = 600 
# TODO: implement a batter session timeout function
# def handler(signum, frame):
#     """This function runs when the alarm goes off."""
#     raise TimeoutError

#TODO: fix the internet health monitor later
# def net_interrupt():
#     """
#     displays fancy waiting animation
#     returns to last cursor position after the animation
#     """
#     while True:
#         if not internet_available.is_set():
#             cols, rows = shutil.get_terminal_size()
#             sys.stdout.write("\033[s")
#             sys.stdout.flush()
#             # sys.stdout.write(f"\033[{rows};1H")
#             # sys.stdout.flush()
#             sys.stdout.write("\033[S")
#             sys.stdout.write(f"\033[{rows};1H\033[2K")
#             sys.stdout.flush()
#             with console.status("waiting for connection...."):
#                 while not internet_available.wait():  
#                     continue
#             sys.stdout.write("\033[T")
#             # sys.stdout.write("\033[M")
#             sys.stdout.write("\033[u")
#             sys.stdout.flush()  
#             # sys.stdout.write("\033[u")
#             # sys.stdout.flush()

# def connection_monitor():
#     last_state = True
#     while True:
#         connected = True
#         try:
#             socket.create_connection(("8.8.8.8", 53), timeout=1)
#         except OSError:
#             connected = False

#         if connected and not last_state:
#             internet_available.set()
#             last_state = True

#         elif not connected and last_state:
#             internet_available.clear()
#             last_state = False

#         time.sleep(1)

def acquire_lock():
    """
    This ensures the manager can only run one at a time
    prevent race condition of having duplicate managers
    """
    lock_file_path = "/tmp/platform_manager.lock"
    lock_file = open(lock_file_path, 'w')
    
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        return lock_file 
    
    except IOError:
        console.print("[bold red]❌ Error: Another instance of the Manager is already running![/bold red]")
        console.print("[dim]Please close the other terminal or wait for the deployment to finish.[/dim]")
        sys.exit(1)


def main():
    

    # PRE-FLIGHT RESET
    with console.status("[bold green]Initializing secure environment...[/bold green]"):
        subprocess.run(["bw", "logout"], capture_output= True)
        subprocess.run(["sudo", "pkill", "tailscaled"], capture_output= True)
        time.sleep(1)

    console.rule("[bold blue]Cloith Platform Manager[/bold blue]")
    try:
        # 1. AUTHENTICATION (The Gatekeeper)
        session_key = login_to_bitwarden()

        if not session_key:
            sys.exit(1)

        # 2. SYNC TO ENSURE LATEST VAULT DATA
        with console.status("[bold yellow]Syncing Bitwarden vault...[/bold yellow]"):
            sync_bitwarden_vault(session_key)

        # 3. TAILSCALE NETWORK CHECK
        network_check(session_key)

        template = scan_and_provision()

        while True:
            choice = questionary.select(
                "Main Menu - Select an Action:",
                choices=[
                    "🛠️ Redeploy: (Runs the main playbook to apply changes)",
                    "🔑 View Session Info",
                    "❌ Exit Manager"
                ]
            ).ask()

            if choice == "❌ Exit Manager" or choice is None:
                console.print("[yellow]Shutting down manager...[/yellow]")
                break 

            elif choice == "🛠️ Redeploy: (Runs the main playbook to apply changes)":
                deploy_template(template, session_key)
                input("\nPress Enter to return to menu...") 

            elif choice == "🔑 View Session Info":
                console.print(f"Current Session: [cyan]{session_key[:12]}***[/cyan]")
                input("\nPress Enter to return to menu...")

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Force shutdown (Ctrl+C).[/yellow]")
    except TimeoutError:
        console.print("\n[red]⏰ Session timed out due to inactivity.[/red]")
        
if __name__ == "__main__":
    manager_lock = acquire_lock()
    try:
        main()
    finally:
            manager_lock.close()
            if os.path.exists("/tmp/platform_manager.lock"):
                os.remove("/tmp/platform_manager.lock")
            with console.status("[bold yellow]Logging out of Tailscale...[/bold yellow]"):
                subprocess.run(["sudo", "tailscale", "logout"], capture_output=True)
            with console.status("[bold yellow]🔥 Burning the bridge (Shutting down Tailscale)...[/bold yellow]"):
                subprocess.run(["sudo", "pkill", "tailscaled"], capture_output=True)
            console.print("[green]✓ Tunnel destroyed. Attack surface minimized.[/green]")
            with console.status("[bold yellow]Logging out of bitwarden...[/bold yellow]"):
                subprocess.run(["bw", "logout"], capture_output=True)
            console.print("[bold red]🔒 Session terminated. Goodbye![/bold red]")

        