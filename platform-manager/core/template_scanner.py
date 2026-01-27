import json
import os
import questionary
from providers.bitwarden.vault import get_secret
from rich.console import Console
from pathlib import Path

console = Console()
TEMPLATES_DIR = Path("templates")
STATE_FILE = Path("platform-manager/.template_state.json")

def load_template_state():
    state_path = Path("platform-manager/.template_state.json")

    # 1. Ensure the parent directory exists (platform-manager/)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. If the file is missing, create it with a default structure
    if not state_path.exists():
        default_state = {"active_template": None, "history": []}
        with open(state_path, 'w') as f:
            json.dump(default_state, f, indent=4)
        return default_state
    
    # 3. Read the existing file
    try:
        with open(state_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Handle cases where the file exists but is corrupted/empty
        return {"active_template": None, "history": []}

def load_requirements(active_template):
    req_file = Path(f"templates/{active_template}/requirements.json")

    if not req_file.exists():
        console.print(f"[red]✘ Requirement file not found for template {active_template}.[/red]")
        return False
    
    with open(req_file, "r") as f:
        data = json.load(f)
        return data.get("requirements", [])

def save_template_state(new_state_data):
    """Saves the current state to the hidden JSON file."""
    # Load existing state first to avoid wiping other keys
    state = {}
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
    
    # Update with new values
    state.update(new_state_data)
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def handle_template_creation():
    """Asks for a template name and scaffolds the folder structure."""
    name = questionary.text("What is the name of your new template?").ask()
    
    if not name:
        console.print("[red]Creation cancelled.[/red]")
        return False

    # Standardize the folder name (lowercase, no spaces)
    folder_name = name.lower().replace(" ", "-")
    target_path = TEMPLATES_DIR / folder_name

    if target_path.exists():
        console.print(f"[red]Error: {folder_name} already exists![/red]")
        return False

    # 1. Create the directories
    target_path.mkdir(parents=True)
    (target_path / "tasks").mkdir()

    # 2. Scaffold default files
    # Requirements file (where you'll list API keys needed)
    requirements_content = {
        "api_keys": ["bw_session_key"], 
        "description": f"Infrastructure for {name}"
    }
    
    with open(target_path / "requirements.json", 'w') as f:
        json.dump(requirements_content, f, indent=4)

    # Main Ansible Playbook entry point
    playbook_path = target_path / "main.yml"
    playbook_path.write_text("---\n- name: Main Provisioning\n  hosts: all\n  tasks: []")

    console.print(f"[green]✔ Template '{folder_name}' scaffolded successfully![/green]")
    
    # 3. Automatically set this as the active template
    save_template_state({"active_template": folder_name})
    return True

def requirements_met(requirements, session_key):
    for req in requirements:
        console.print(f"\n[bold]Checking {req}...[/bold]")
        get_secret(req, session_key)
    return None

def scan_and_provision():
    state = load_template_state()
    active_template = state.get("active_template")

    if not active_template:
        console.print("[yellow]⚠ No active template detected.[/yellow]")
        
        # 1. Scan the folder for directories
        available_folders = [
            f.name for f in TEMPLATES_DIR.iterdir() 
            if f.is_dir() and not f.name.startswith('.')
        ]
        
        # 2. Build choices: Real folders + "Create Template" action
        choices = available_folders + [questionary.Separator(), "Create New Template"]
        
        selected = questionary.select(
            "Select an infrastructure template to provision:",
            choices=choices
        ).ask()

        if selected == "Create New Template":
            # Trigger your creation logic here
            return handle_template_creation() 
        elif selected:
            # Update the state file with the user's choice
            active_template = selected
            save_template_state({"active_template": active_template})
            console.print(f"[green]✔ Provisioning started for: {active_template}[/green]")
        else:
            return False # User cancelled (Ctrl+C)

    # 3. Proceed with the logic for the (now confirmed) active template
    console.print(f"[green]✓ Active template: {active_template}[/green]")

    return active_template
    
    