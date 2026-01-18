import pexpect
import questionary
import re
from rich.console import Console

console = Console()

def login_to_bitwarden():

    while True:
        # Spawn inside the loop so each attempt is fresh
        child = pexpect.spawn("bw login", encoding='utf-8', timeout=30)
        
        try:
            # Step 1: Identity
            email = questionary.text(
                "Enter your Bitwarden Email:",
                validate=lambda text: True if "@" in text and "." in text else "Please enter a valid email"
            ).ask()
            child.sendline(email)

            password = questionary.password(
                "Enter your Master Password:",
                validate=lambda text: True if text.strip() else "Must not be empty"
            ).ask()
            child.sendline(password)

            # Step 2: Check for 2FA or Direct Success
            with console.status("[bold blue]Authenticating...[/bold blue]"):
                next_step = child.expect([
                    "Enter OTP sent to login email:", 
                    "Two-step login code:",
                    "You are logged in!",
                    "Invalid master password",
                    "The Email field is not a valid e-mail address.",
                    pexpect.EOF
                ])

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
            child.expect(pexpect.EOF)     
            output = child.before 
            match = re.search(r'BW_SESSION="([^"]+)"', output)
            
            if match:
                session_key = match.group(1)
                console.print("[green]✔ Login Successful and Key Captured![/green]")
                return session_key 
            else:
                console.print("[red]✘ Could not extract session key.[/red]")
                return False

        except (pexpect.TIMEOUT, pexpect.EOF):
            console.print("[red]✘ Error: Bitwarden connection failed.[/red]")
            return False
        finally:
            child.close()