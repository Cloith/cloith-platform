
import sys
import requests
import subprocess
from rich.console import Console

console = Console()

def validate_hostinger_token(token):
    """
    Checks if the Hostinger token is valid by hitting a lightweight endpoint.
    """
    url = "https://api.hostinger.com/v1/usage" # Example lightweight endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        # 200 means it's good, 401/403 means the token is "hello" or expired
        return response.status_code == 200
    except Exception:
        return False

def validate_ts_auth(key):
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
    except Exception:
        console.print("[red]Error: Unable to reach Tailscale API for validation.[/red]")
        sys.exit(1)
    if response.status_code == 200:
        return True
    return False