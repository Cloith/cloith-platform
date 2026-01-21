import json
import sys
from providers.bitwarden.vault import get_secret
from rich.console import Console
from pathlib import Path


console = Console()

def load_template_state():
    state_path = Path("platform-manager/.template_state.json")

    if not state_path.exists():
        console.print("[yellow]⚠ No state file found. Please select a template first.[/yellow]")
        sys.exit(1)
    with open(state_path, 'r') as f:
            return json.load(f)

    # To do: Implement template selection flow here
    return None

def load_requirements(active_template):
    req_file = Path(f"infrastructure-collections/{active_template}/requirements.json")

    if not req_file.exists():
        console.print(f"[red]✘ Requirement file not found for template {active_template}.[/red]")
        return False
    
    with open(req_file, "r") as f:
        data = json.load(f)
        return data.get("requirements", [])



def scan_and_provision(session_key):
    state = load_template_state()

    # Taking the first active template for now
    active_template = state.get("active_templates", [None])[0]

    if active_template:
        console.print(f"[green]✓ Active template: {active_template}[/green]")
        requirements = load_requirements(active_template)
        secret = requirements_met(requirements, session_key)
        console.print(f"[blue]ℹ Loaded requirements for {active_template}: {requirements[1]}[/blue]")
        return True
    else:
        console.print("[red]✘ No active templates found. Please provision an environment first.[/red]")
        return False
    

def requirements_met(requirements, session_key):
    for req in requirements:
        console.print(f"\n[bold]Checking {req}...[/bold]")
        secret_value = get_secret(req, session_key)
    return None
    
    