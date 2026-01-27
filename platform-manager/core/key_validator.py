
import sys
import subprocess
import requests
import pexpect
from rich.console import Console

console = Console()

def validate_key(name, token):
    """
    Validates the given key based on its type.
    """
    if name == "hostinger_token":
        return validate_hostinger_token(token)
    elif name == "tailscale_api_key":
        return validate_ts_api(token)
    elif name == "tailscale_auth_key":
        return validate_ts_auth(token)
    elif name == "username":
        console.print(f"[green]✓ Username: [yellow]{token}[/yellow] fecthed from vault.[/green]")
        return True  # No validation needed for username
    

def validate_hostinger_token(token):
    url = "https://developers.hostinger.com/api/billing/v1/subscriptions" # Example lightweight endpoint
    headers = {"Authorization": f"Bearer {token}"} 
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code !=200:
            return False
        return True
    except Exception:
        console.print("[red]Error: Unable to reach Tailscale API for validation.[/red]")
        sys.exit(1)
    return False


def validate_ts_api(token):
    url = "https://api.tailscale.com/api/v2/tailnet/-/keys"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code !=200:
            return False
        return True
    except Exception:
        console.print("[red]Error: Unable to reach Tailscale API for validation.[/red]")
        sys.exit(1)
    return False

def validate_ts_auth(token):
    # Pass as a LIST, not a string. 'sudo' is the command, the rest are args.
    # This prevents the token from ever being interpreted as code.
    args = ["tailscale", "login", "--authkey", token]
    
    try:
        child = pexpect.spawn("sudo", args, timeout=15, encoding='utf-8')
        index = child.expect(["invalid key", "backend error", pexpect.EOF, pexpect.TIMEOUT])

        if index == 0 or index == 1:
            return False 
                
        if index == 2:
            return True 
        
        if index == 3:
            console.print("[yellow]! Validation timed out.[/yellow]")
            return False

    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        return False
