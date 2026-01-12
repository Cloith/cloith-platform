import os
import pexpect
import subprocess
import questionary
from rich.console import Console

console = Console()

def login_to_bitwarden(email, password):
    env = os.environ.copy()
    env["BW_PASSWORD"] = password
    
    # Start the process in a controlled 'pseudo-terminal'
    # This prevents the CLI from 'glitching' the screen
    child = pexpect.spawn(
        f"bw login {email} --passwordenv BW_PASSWORD", 
        env=env, 
        encoding='utf-8'
    )

    # We tell Python to wait and look for specific patterns
    # 0: The OTP prompt
    # 1: Success message
    # 2: Already logged in
    # pexpect.EOF: The process finished
    index = child.expect([
        "Enter OTP sent to login email:", 
        "Success", 
        "You are already logged in", 
        pexpect.EOF
    ])

    if index == 0:
        # 1. Detect OTP prompt -> Trigger our own clean Questionary prompt
        otp_code = questionary.text("Check your email for OTP and paste it here:").ask()
        
        # 2. Send the code back to the Bitwarden CLI
        child.sendline(otp_code)
        
        # 3. Wait for it to finish without printing the output to terminal
        child.expect(pexpect.EOF)
        console.print("[green]✔ OTP Accepted and Login Successful![/green]")
    
    elif index == 1 or index == 2:
        console.print("[blue]ℹ Already logged in or Success.[/blue]")
    
    child.close()
    return True

def main():
    console.print("[bold blue]Cloith Platform Manager[/bold blue]", justify="center")
    
    # Task 1: Get Credentials
    email = questionary.text("Enter your Bitwarden Email:").ask()
    password = questionary.password("Enter your Master Password:").ask()

    # Task 2: Inject and Login
    if email and password:
        login_to_bitwarden(email, password)
    else:
        console.print("[red]Missing credentials.[/red]")

if __name__ == "__main__":
    main()