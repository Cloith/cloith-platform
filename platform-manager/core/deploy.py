import subprocess
import os
from rich.console import Console
from providers.bitwarden.vault import get_secret

console = Console()

def deploy_template(template_name, session_key):

    playbook_path = f"templates/{template_name}/rebuild-all.yml"

    net_auth_key = get_secret("tailscale_auth_key", session_key)
    net_api_key = get_secret("tailscale_api_key", session_key)
    vps_api_key = get_secret("hostinger_token", session_key)
    user = get_secret("username", session_key)
    
    if not os.path.exists(playbook_path):
        print(f"Error: Template {template_name} not found!")
        return

    print(f"🚀 Deploying {template_name}...")

    command = [
        "ansible-playbook", 
        playbook_path,
        "-e", f"tailscale_auth_key={net_auth_key} "
              f"tailscale_api_key={net_api_key} "
              f"hostinger_api_token={vps_api_key} "
              f"remote_user={user}"
    ]

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge error and output into one stream
            text=True,                 # Treat output as strings, not bytes
            bufsize=1                  # Line-buffered for immediate updates
        )
        # Stream the output line-by-line
        for line in iter(process.stdout.readline, ""):
            # You can use rich to color specific Ansible keywords
            clean_line = line.strip()
            if "ok:" in clean_line:
                console.print(f"[green]{clean_line}[/green]")
            elif "changed:" in clean_line:
                console.print(f"[yellow]{clean_line}[/yellow]")
            elif "failed:" in clean_line or "unreachable:" in clean_line:
                console.print(f"[red][bold]{clean_line}[/bold][/red]")
            else:
                console.print(f"[dim]{clean_line}[/dim]")
    
        process.wait() # Ensure the process is fully closed

        if process.returncode == 0:
            console.print("✅ [bold green]Deployment Successful![/bold green]")
        else:
            console.print("❌ [bold red]Deployment Failed![/bold red]")

    except subprocess.CalledProcessError:
        print("❌ Deployment Failed. Check Ansible logs.")