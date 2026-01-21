
import sys
import requests
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

def validate_hostinger_token(token):
    url = "https://developers.hostinger.com/api/billing/v1/subscriptions" # Example lightweight endpoint
    headers = {"Authorization": f"Bearer {token}"} 
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code !=200:
            console.print("[red]✘ Hostinger Token is invalid.[/red]")
            return False
        console.print(f"[green]✓ Hostinger Token is valid.[/green]")
        return True
    except Exception:
        return False


def validate_ts_api(token):
    url = "https://api.tailscale.com/api/v2/tailnet/-/keys"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code !=200:
            console.print("[red]✘ Tailscale API Key is invalid.[/red]")
            return False
        console.print(f"[green]✓ Tailscale API Key is valid.[/green]")
        return True
    except Exception:
        console.print("[red]Error: Unable to reach Tailscale API for validation.[/red]")
        sys.exit(1)

    return False