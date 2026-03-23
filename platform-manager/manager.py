import fcntl
import os
import sys
from rich.console import Console
from textual.app import App
from screens.loading_screen import LoadingScreen
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.hostinger.provisioning_manager_screen import ProvisioningManagerScreen
from screens.hostinger.vps_picker_screen import VPSPickerScreen
from screens.manual_deployment_screen import ProviderSelectionScreen
from providers.bitwarden.bitwarden_vault_service import BitwardenVaultService
from services.service_factory import get_vault_service

console = Console()

class PlatformManager(App):
    def on_mount(self) -> None:
        self.app.bw_session = "2riWMGIOkZEUBhN58fdxaqPvofKiBsR/wpxa37OpW5TqOcrMP7V3mm5Y/XFrX3JUxtfKmw21tZGJ6lHQmNbfg=="
        vault_service = get_vault_service("bitwarden", self.app)
        self.push_screen(DashboardScreen(vault_service))

    @staticmethod
    def acquire_lock():
        """Ensures only one instance runs, with stale lock detection."""
        lock_file_path = "/tmp/platform_manager.lock"
        lock_file = open(lock_file_path, 'a+')
        
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            lock_file.seek(0)
            content = lock_file.read().strip()
            
            if content.isdigit():
                old_pid = int(content)
                try:
                    os.kill(old_pid, 0) 
                except OSError:
                    console.print(f"[yellow]Detected stale lock from dead PID {old_pid}. Cleaning up...[/yellow]")
                    lock_file.close()
                    try:
                        os.remove(lock_file_path)
                    except: pass
                    return PlatformManager.acquire_lock()

            console.print(f"[bold red]Error: Another instance (PID {content}) is already running![/bold red]")
            sys.exit(1)

        lock_file.seek(0)
        lock_file.truncate()
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        os.fsync(lock_file.fileno()) 
        return lock_file

# def cleanup_session(lock_file=None):
#     """The master cleanup function called by finally OR signals."""
#     with console.status("[bold yellow]Cleaning up... please wait[/bold yellow]"):
#         subprocess.run(["sudo", "tailscale", "logout"], capture_output=True)
#         subprocess.run(["sudo", "pkill", "tailscaled"], capture_output=True)
#         subprocess.run(["bw", "logout"], capture_output=True)
#         subprocess.run(["sudo", "pkill", "dockerd"], capture_output=True)
#         subprocess.run(["sudo", "rm", "-f", "/var/run/docker.pid", "/var/run/docker.sock"], capture_output=True)

#     if lock_file:
#         lock_file.close()
#     if os.path.exists("/tmp/platform_manager.lock"):
#         os.remove("/tmp/platform_manager.lock")
        
#     console.print("[bold red]🔒 Session terminated. Goodbye![/bold red]")
#     sys.exit(0)

# def signal_handler(sig, frame):
#     cleanup_session(manager_lock)

if __name__ == "__main__":
    # signal.signal(signal.SIGINT, signal_handler)
    # signal.signal(signal.SIGTERM, signal_handler)

    manager_lock = PlatformManager.acquire_lock()
    
    app = PlatformManager()
    app.run()
    # try:
    #     app.run()
    # except Exception as e:
    #     console.print(f"[red]Application Error: {e}[/red]")
    # finally:
    #     cleanup_session(manager_lock)
    #     None