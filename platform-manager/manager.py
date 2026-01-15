import sys
import signal
import pexpect
from rich.console import Console
import questionary
from auth import login_to_bitwarden 

console = Console()

# Define the timeout 
IDLE_TIMEOUT = 600 # 10 minutes

def handler(signum, frame):
    """This function runs when the alarm goes off."""
    raise TimeoutError

def main():
    console.rule("[bold blue]Cloith Platform Manager[/bold blue]")
    
    try:
        # 1. AUTHENTICATION (The Gatekeeper)
        session_key = login_to_bitwarden()
            
        if not session_key:
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
        # THE CLEANUP (Only runs once when the loop breaks)
        with console.status("[bold yellow]Logging out of bitwarden...[/bold yellow]"):
            pexpect.run("bw logout")
        console.print("[bold red]🔒 Session terminated. Goodbye![/bold red]")

if __name__ == "__main__":
    main()