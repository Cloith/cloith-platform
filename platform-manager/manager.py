import pexpect
import questionary
import re
from rich.console import Console
import sys

console = Console()

def login_to_bitwarden():
    while True:
        child = pexpect.spawn("bw login", encoding='utf-8', timeout=30)
        
        try:
            # Step 1: Identity
            email = questionary.text("Enter your Bitwarden Email:").ask()
            if email is None: return False
            child.sendline(email)

            password = questionary.password("Enter your Master Password:").ask()
            if password is None: return False
            child.sendline(password)

            
            # Step 2: Check for 2FA or Direct Success
            next_step = child.expect([
                "Enter OTP sent to login email:", 
                "Two-step login code:",
                "You are logged in!",
                "Invalid master password",
                "The Email field is not a valid e-mail address.",
                pexpect.EOF
            ])
            message = child.before 
            print(f"DEBUG: Bitwarden said: {message}")

            if next_step in [0, 1]:
                otp_code = questionary.text("Enter your 2FA/OTP code:").ask()
                if otp_code is None: return False
                child.sendline(otp_code)
                child.expect("You are logged in!")
            
            elif next_step == 3:
                console.print("[red]✘ Invalid Master Password.[/red]")
                if not questionary.confirm("Try again?").ask(): return False
                continue
            elif next_step == 4:
                console.print("[red]✘ Invalid Email.[/red]")
                if not questionary.confirm("Try again?").ask(): return False
                continue

            # Step 3: Capture the Key
            # We combine the buffers to ensure the regex finds the string
            output = child.before + child.after
            match = re.search(r'BW_SESSION="([^"]+)"', output)
            print(match)
            
            if match:
                session_key = match.group(1)
                console.print("[green]✔ Login Successful and Key Captured![/green]")
                return session_key # Return the actual string
            else:
                console.print("[red]✘ Could not extract session key.[/red]")
                return False

        except (pexpect.TIMEOUT, pexpect.EOF):
            console.print("[red]✘ Error: Bitwarden connection failed.[/red]")
            return False
        finally:
            child.close() # Clean up the pexpect process, but NOT 'bw logout' yet

def main():
    console.rule("[bold blue]Cloith Platform Manager[/bold blue]")
    
    # We store the key here in the main process memory
    session_key = login_to_bitwarden()
    
    if not session_key:
        console.print("[red]Exiting Manager: Authentication Required.[/red]")
        sys.exit(1)
    
    try:
        # ---------------------------------------------------------
        # THE REST OF YOUR APP LIVES HERE
        # ---------------------------------------------------------
        console.print("[bold green]Welcome to the Dashboard![/bold green]")
        console.print(f"Active Session: [dim]{session_key[:10]}...[/dim]")
        
        # Add a menu or your automation logic here
        
    finally:
        # This is the "Zero Secret" cleanup
        # It runs only once when the manager is finally closed
        pexpect.run("bw logout")
        console.print("\n[yellow]🔒 Logged out. Local identity wiped. Session terminated.[/yellow]")

if __name__ == "__main__":
    main()