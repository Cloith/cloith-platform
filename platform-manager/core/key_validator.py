import sys
import os
import requests
import pexpect
from rich.console import Console

console = Console()

def validate_key(name, token):
    """
    Validates the given key based on its type.
    """
    if name == "hostinger_token":
        valid = validate_hostinger_token(token)
        token = None
        return valid
    elif name == "tailscale_api_key":
        valid = validate_ts_api(token)
        token = None
        return valid
    elif name == "tailscale_auth_key":
        valid = validate_ts_auth(token)
        token = None
        return valid
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
    targeted_env = {
                "TS_AUTHKEY": token,
                "PATH": "/usr/sbin:/usr/bin:/sbin:/bin", 
                "TERM": os.environ.get("TERM", "xterm-256color")
            }
    cmd = ["sudo", "tailscale", "login", "--authkey=$TS_AUTHKEY"]
    
    try:
        child = pexpect.spawn(f"sh -c '{cmd}'", env=targeted_env, timeout=60, encoding='utf-8')
        index = child.expect(["invalid key", "backend error", pexpect.EOF, pexpect.TIMEOUT])

        if index in [0,1]:
            return False  
        if index == 2:
            return True
        if index == 3:
            console.print("[yellow]! Validation timed out.[/yellow]")
            return False

    except Exception as e:
        console.print(f"[red]Error during validation: {e}[/red]")
        return False
    finally:
       token = None