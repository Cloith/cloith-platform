import pexpect
import questionary
from rich.console import Console
import sys

console = Console()

def login_to_bitwarden():
    while True:  # Use a loop instead of recursion for cleaner exits
        child = pexpect.spawn("bw login", encoding='utf-8', timeout=30)
        
        try:
            # Step 1: Initial Check
            index = child.expect(["Email address:", "You are already logged in", pexpect.EOF])

            if index == 1:
                console.print("[blue]ℹ Already logged in.[/blue]")
                return True
            
            if index == 0:
                email = questionary.text(
                    "Enter your Bitwarden Email:",
                    validate=lambda text: True if "@" in text else "Please enter a valid email"
                ).ask()
                
                # If user hits Ctrl+C or cancels the questionary prompt
                if email is None: return False
                
                child.sendline(email)

                password = questionary.password("Enter your Master Password:").ask()
                if password is None: return False
                
                child.sendline(password)

                # Step 3: Result Validation
                next_step = child.expect([
                    "Enter OTP sent to login email:", 
                    "Two-step login code:",
                    "You are logged in!",
                    "Invalid master password",
                    "The Email field is not a valid e-mail address."
                ])

                if next_step in [0, 1]:
                    otp_code = questionary.text("Enter your 2FA/OTP code:").ask()
                    if otp_code is None: return False
                    child.sendline(otp_code)
                    child.expect("You are logged in!")
                    console.print("[green]✔ OTP Accepted and Login Successful![/green]")
                    return True
                
                elif next_step == 2:
                    console.print("[green]✔ Login Successful![/green]")
                    return True
                
                elif next_step == 3:
                    console.print("[red]✘ Invalid Master Password.[/red]")
                
                elif next_step == 4:
                    console.print("[red]✘ Invalid Email Address.[/red]")

                # If we reach here, a login error happened. Ask to retry.
                if not questionary.confirm("Would you like to try again?").ask():
                    console.print("[yellow]⚠ Login aborted by user.[/yellow]")
                    return False  # Breaks the loop and exits function

        except pexpect.TIMEOUT:
            console.print("[red]✘ Error: Bitwarden timed out.[/red]")
            return False
        except pexpect.EOF:
            console.print("[red]✘ Error: Bitwarden process ended unexpectedly.[/red]")
            return False
        finally:
            child.close() # Ensures the process is killed before the loop restarts

def main():
    console.rule("[bold blue]Cloith Platform Manager[/bold blue]")
    
    success = login_to_bitwarden()
    
    if not success:
        console.print("[red]Exiting Manager: Authentication Required.[/red]")
        sys.exit(1)
    
    # Continue with the rest of your app here
    console.print("[bold green]Welcome to the Dashboard![/bold green]")

if __name__ == "__main__":
    main()