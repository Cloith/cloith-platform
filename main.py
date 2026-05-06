from rich.console import Console
from textual.app import App
from textual.events import Resize
from screens.provisioning_manager import ProvisioningManagerScreen
from services.service_factory import get_vault_service

class PlatformManager(App):
    def __init__(self) -> None:
        super().__init__()
        self.provider_token = None
        self.vault_session = None
        self.vault_service = None
        self.provider_service = None

    def on_mount(self) -> None:
        vault_service = get_vault_service("bitwarden", self)
        self.vault_service = vault_service
        self.push_screen(ProvisioningManagerScreen())

    def on_resize(self, event: Resize) -> None:
        self.refresh()

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