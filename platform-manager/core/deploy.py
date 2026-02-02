import pexpect
import json
import tempfile
import shlex
import os
import re
import sys
from rich.console import Console
from providers.bitwarden.vault import get_secret

console = Console()

def deploy_template(template_name, session_key):
    # TODO: make it async, avoided it because of potential race condition caused by the auto validation from the get_secret function
    net_auth_key = get_secret("tailscale_auth_key", session_key)
    net_api_key = get_secret("tailscale_api_key", session_key)
    vps_api_key = get_secret("hostinger_token", session_key)
    user = get_secret("username", session_key)

    project_root = f"/workspaces/cloith-platform/templates/{template_name}"
    
    # 1. Prepare JSON
    extra_vars = {
        "tailscale_auth_key": net_auth_key,
        "tailscale_api_key": net_api_key,
        "hostinger_api_token": vps_api_key,
        "admin_username": user
    }
    vars_json = json.dumps(extra_vars)

    # 2. Setup the RAM Pipe (FIFO)
    tmpdir = tempfile.mkdtemp()
    fifo_path = os.path.join(tmpdir, "vars.fifo")
    os.mkfifo(fifo_path)

    # 3. Construct command with the actual path
    command_str = shlex.join([
        "ansible-playbook", 
        "rebuild-all.yml",
        "-e", f"@{fifo_path}"  
    ])

    child = None # Initialize for the 'finally' block
    try:
        console.print(f"🚀 [bold cyan]Deploying {template_name} via RAM Pipe...[/bold cyan]")

        # 4. Start Ansible FIRST (It will wait for data from the FIFO)
        child = pexpect.spawn(command_str, cwd=project_root, encoding='utf-8', timeout=None)
        child.setecho(False) # Prevent secret echo

        # 5. Shove data into the pipe
        # This will unblock Ansible and let it start the playbook
        with open(fifo_path, 'w') as fifo:
            fifo.write(vars_json)

        while True:
            try:
                line = child.readline()
                if not line:
                    break
                
                # 1. Strip ANSI escape sequences (the [0;32m stuff)
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                clean_line = ansi_escape.sub('', line).strip()
                
                if not clean_line:
                    continue

                # 2. Filter out the vars_json leak
                if vars_json[:20] in clean_line:
                    continue
                
                # 3. Now your logic works on clean text
                if "ok:" in clean_line:
                    console.print(f"[green]{clean_line}[/green]")
                elif "changed:" in clean_line:
                    console.print(f"[yellow]{clean_line}[/yellow]")
                elif "failed:" in clean_line or "unreachable:" in clean_line:
                    console.print(f"[red][bold]{clean_line}[/bold][/red]")
                else:
                    console.print(f"[dim]{clean_line}[/dim]")
            except pexpect.EOF:
                break

        child.wait() 
        if child.exitstatus == 0:
            console.print("✅ [bold green]Deployment Successful![/bold green]")
        else:
            console.print(f"❌ [bold red]Deployment Failed with status {child.exitstatus}![/bold red]")

    except Exception as e:
        console.print(f"❌ [bold red]An error occurred:[/bold red] {e}")
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Force shutdown (Ctrl+C).[/yellow]")
        sys.exit(1)
    finally:
        # 6. Cleanup the evidence
        if os.path.exists(fifo_path):
            os.remove(fifo_path)
        if os.path.exists(tmpdir):
            os.rmdir(tmpdir)
        if child and child.isalive():
            child.close()
        