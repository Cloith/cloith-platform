import subprocess
import json
import questionary
import sys
from rich.console import Console
from core.key_validator import validate_key



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
    
def update_key(new_value, session_key, name):
    """
    Updates an existing secret in Bitwarden with a new value.
    """
    
    try:
        # 1. Get the existing item to find its unique ID
        # We search by name
        get_cmd = ["bw", "get", "item", name, "--session", session_key]
        item_data = json.loads(subprocess.check_output(get_cmd))
        item_id = item_data['id']

        # 2. Update the secret value in the JSON object
        # In a 'login' type item, the password field is usually where keys go
        if item_data.get('login'):
            item_data['login']['password'] = new_value

        # 3. Bitwarden 'edit' command requires the JSON to be encoded
        # We turn the dict back to a string, then to Base64
        json_string = json.dumps(item_data)
        encode_process = subprocess.run(
            ["bw", "encode"], 
            input=json_string, 
            capture_output=True, 
            text=True, 
            check=True
        )
        encoded_json = encode_process.stdout.strip()

        # 4. Push the update back to Bitwarden
        edit_cmd = ["bw", "edit", "item", item_id, encoded_json, "--session", session_key]
        
        
        subprocess.run(edit_cmd, check=True, capture_output=True)
        
        console.print(f"[green]✔ Vault item '{name}' updated successfully![/green]")
        return True

    except Exception as e:
        console.print(f"[red]✘ Failed to update vault: {e}[/red]")
        return False

def get_secret(item_name, session_key=None):
    cmd = ["bw", "get", "item", item_name, "--session", session_key]

    while True:
        with console.status(f"[bold yellow]Fetching '{item_name}' from Bitwarden...[/bold yellow]") as status:
            result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if the error is specifically "Not found."
        if "Not found" in result.stderr:
            console.print(f"Item '{item_name}' not found. Triggering creation logic...")
            while True:
                value = questionary.password(
                    f"Enter the value for '{item_name}':",
                    validate=lambda text: True if text.strip() else "Must not be empty"    
                ).ask()

                if not value:
                    console.print("No value provided. Aborting item creation.")
                    sys.exit(1)

                with console.status(f"[bold yellow]Validating '{item_name}'...[/bold yellow]"):
                    valid = validate_key(item_name, value)

                if not valid:
                    console.print(f"[red]✘ {item_name} is Invalid.[/red]")
                    if not questionary.confirm("Try again?").ask(): sys.exit(1)
                    continue

                val = create_bitwarden_item(item_name, value, session_key)
  
                console.print(f"[green]✓ {item_name} is Valid and ready to use.[/green]")
                return val
            

        data = json.loads(result.stdout)
        key = data.get('login', {}).get('password')    
        
        with console.status(f"[bold yellow]Validating '{item_name}'...[/bold yellow]"):
            valid = validate_key(item_name, key)

        if not valid:
            while not valid:
                console.print(f"[red]✘ {item_name} is Invalid.[/red]")
                console.print("Triggering update logic...")
                
                value = questionary.password(
                    f"Enter the value for '{item_name}':",
                    validate=lambda text: True if text.strip() else "Must not be empty"
                ).ask()
                if not value:
                    console.print("No value provided. Aborting item creation.")
                    sys.exit(1) 
                with console.status(f"[bold yellow]Validating '{item_name}'...[/bold yellow]"):
                    valid = validate_key(item_name, value)
                if not valid:
                    console.print(f"[red]✘ {item_name} is Invalid.[/red]")
                    if not questionary.confirm("Try again?").ask(): sys.exit(1)
                    continue
                with console.status(f"[bold yellow]Updating '{item_name}' in Bitwarden...[/bold yellow]"):
                    update_key(value, session_key, name=item_name)
                    valid = True
                    console.print(f"[green]✓ {item_name} is Valid and updated in vault.[/green]")
            continue  # Retry fetching after update
        return key
        