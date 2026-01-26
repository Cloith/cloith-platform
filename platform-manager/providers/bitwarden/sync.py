import subprocess
import sys
import time
from rich.console import Console

console = Console()

def sync_bitwarden_vault(session_key, retries=2):
    """Resilient sync that handles minor CLI quirks."""
    for attempt in range(retries + 1):
        result = subprocess.run(
            ["bw", "sync", "--session", session_key],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True
            
        # Check if the error is actually just a warning
        stderr = result.stderr.lower()
        if "already synced" in stderr:
            return True
            
        # If we have retries left, wait a moment
        if attempt < retries:
            time.sleep(1)
            continue
            
        # If it truly failed after retries, log the error
        console.print(f"[red]✗ Sync Failed:[/red] {result.stderr.strip()}")
        return False