from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button, LoadingIndicator
from textual.containers import Container, Horizontal
from custom_widgets.password_input import PasswordInput
from services.base_vault import VaultStatus
from services.base_vps import VPSStatus


class PasswordModal(ModalScreen[str]):
    """A pop-up modal to capture the Master Password."""
    
    DEFAULT_CSS = """
    PasswordModal {
        align: center middle;
    }

    #modal-container {
        height: 13;
        width: 50;
        border: round $accent;
        align: center middle;
    }

    PasswordModal #loading-animation {
        height: 3;
        width: 16;
        color: $accent;
        display: none;
        margin-bottom: 8;
    }

    PasswordModal #button-container {
        height: 5;
        align: center middle;
    }

    PasswordModal #loading-container {
        align: center middle;
    }

    #modal-container.loading #loading-animation {
        display: block;
    }

    #modal-container.loading #button-container {
        display: none;
    }
    """

    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        

    @property
    def current_config(self):
        """Calculates config values dynamically when accessed."""
        if self.mode == "provider":
            return {
                "title": f'Enter New "{self.app.vps_service.provider_name.title()}" API Token',
                "button": "Update Token",
                "service": self.app.check_token 
            }
        # Default/Vault mode
        return {
            "title": "Input Master Password to Continue",
            "button": "Unlock Vault",
            "service": self.app.vault_service.unlock
        }

    def compose(self) -> ComposeResult:
        config = self.current_config
        with Container(id="modal-container"):
            yield Label(config["title"], id="modal-text")
            yield PasswordInput()
            with Horizontal(id="button-container"):
                yield Button("Cancel", variant="error", id="cancel-btn")
                yield Button("Unlock", variant="success", id="unlock-btn")
            with Container(id="loading-container"):
                yield LoadingIndicator(id="loading-animation")

    def on_mount(self) -> None:
        self.container = self.query_one("#modal-container")

    @on(Input.Submitted, "PasswordInput #password")
    @on(Button.Pressed, "#unlock-btn")
    def unlock_button(self) -> None:
        password = self.query_one("PasswordInput").trigger_submit()

        if not password:
            return
        self.query_one("#modal-container").add_class("loading")
        self.call_service(password)
    
    @on(Button.Pressed, "#cancel-btn")
    def cancel_button(self) -> None:
        self.dismiss(None)

    @work
    async def call_service(self, value: str) -> None:
        if self.mode == "vault":
            service_func = self.current_config["service"]
            result = await service_func(value)

            if result in (VaultStatus.SUCCESS, VPSStatus.SUCCESS):
                self.dismiss(result)
            elif result == VaultStatus.WRONG_PASSWORD:
                self.query_one("#modal-container").remove_class("loading")
                
                if result == VaultStatus.WRONG_PASSWORD:
                    error_msg = "[red]Incorrect Master Password[/]"
                elif result == VPSStatus.TOKEN_INVALID:
                    error_msg = "[red]Invalid Provider Token[/]"
                
                self.query_one("PasswordInput #status-message").update(error_msg)

        
        

   