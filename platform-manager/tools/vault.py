import subprocess
import json
import questionary
import os
import sys
from rich.console import Console
import tools.key_validator as validator 


console = Console()

def create_bitwarden_item(item_name, value, session_key):
    """
    Creates a new Login item in Bitwarden following the official CLI workflow.
    """
    # 1. Build the exact template Bitwarden expects for a Login (Type 1)
    item_template = {
        "type": 1,
        "name": item_name,
        "login": {
            "password": value
        }
    }

    # 2. Convert to JSON string
    json_string = json.dumps(item_template)

    try:
        # 3. Step 1: Encode the JSON (The docs say 'bw create' takes encoded JSON)
        encode_result = subprocess.run(
            ["bw", "encode"],
            input=json_string,
            capture_output=True,
            text=True,
            check=True
        )
        encoded_json = encode_result.stdout.strip()

        # 4. Step 2: Create the item using the encoded string
        # Note: The encoded string is passed as an ARGUMENT, not as STDIN for 'create'
        create_cmd = ["bw", "create", "item", encoded_json, "--session", session_key]
        
        with console.status(f"[bold green]Creating Bitwarden item '{item_name}'...[/bold green]"):
            result = subprocess.run(
                create_cmd,
                capture_output=True,
                text=True,
                check=True
            )

        if result.returncode == 0:
            console.print(f"[green]✓ Successfully created: {item_name}[/green]")
            return value
        else:
            console.print(f"[red]Failed to create item in Bitwarden: {result.stderr}[/red]")
            sys.exit(1)

        
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed Bitwarden operation: {e.stderr}[/red]")
        return None

def get_secret(item_name, session_key=None):
    
    cmd = ["bw", "get", "item", item_name, "--session", session_key]
    
    with console.status(f"[bold green]Fetching '{item_name}' from Bitwarden...[/bold green]") as status:
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Check if the error is specifically "Not found."
        if "Not found" in result.stderr:
            console.print(f"Item '{item_name}' not found. Triggering creation logic...")
            value = questionary.password(f"Enter the value for '{item_name}':").ask()
            

            if not value:
                console.print("No value provided. Aborting item creation.")
                sys.exit(1)
            val = create_bitwarden_item(item_name, value, session_key)
            
            console.print(f"[green]✓ Created and stored '{item_name}' in Bitwarden.[/green]")
            return val
            
        else:
            console.print(f"Bitwarden Error: {result.stderr}")
            return None
        
    data = json.loads(result.stdout)

    return data.get('login', {}).get('password')
    

# Dedicated functions for your specific project needs
def fetch_tailscale_auth(session_key):
    return get_secret("ts_auth_key", session_key=session_key)

def get_hostinger_api(session_key):
    return get_secret("Hostinger", session_key=session_key)