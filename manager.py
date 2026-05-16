from rich.console import Console
from textual.app import App
from screens.provisioning_manager import ProvisioningManagerScreen
from services.service_factory import get_vault_service
from services.system.instance_manager import InstanceLock

console = Console()


class PlatformManager(App):
    
    def on_mount(self) -> None:
        vault_service = get_vault_service("bitwarden", self)
        self.vault_service = vault_service
        self.push_screen(ProvisioningManagerScreen())

if __name__ == "__main__":
    try:
        with InstanceLock() as lock:
            PlatformManager().run()
    except Exception as e:
        console.print(f"[bold red]FATAL ERROR:[/bold red] {e}")
    
