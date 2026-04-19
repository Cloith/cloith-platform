from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button, LoadingIndicator
from textual.containers import Container, Horizontal
from custom_widgets import PasswordInput
from models.status import ResponseStatus
from models import OverlayConfig

class PasswordModal(ModalScreen[str]):
    """A pop-up modal for user input prompts"""
    
    DEFAULT_CSS = """
    PasswordModal {
        align: center middle;
    }

    #modal-container {
        max-height: 16;
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

    #retry-btn {
        display: none;
    }
    """

    def __init__(self, mode, config: OverlayConfig):
        super().__init__()
        self.mode = mode
        self.config = config   

    @property
    def current_config(self):
        """Calculates config values dynamically when accessed."""
        if self.mode == "provider":
            return {
                "title": f'Enter New {self.app.vps_service.provider_name.title()} API Token',
                "button": True,
                "placeholder": f"{self.app.vps_service.provider_name.title()} API Token",
                "service": self.app.vps_service.check_token
            }
        # Default/Vault mode
        return {
            "title": "Input Master Password to Continue",
            "button": True,
            "placeholder": "Master Password",
            "service": self.app.vault_service.unlock
        }

    def compose(self) -> ComposeResult:
        config = self.current_config
        with Container(id="modal-container"):
            yield Label(config["title"], id="modal-text")
            yield PasswordInput(placeholder = config["placeholder"])
            with Horizontal(id="button-container"):
                yield Button("Cancel", variant="error", id="cancel-btn")
                yield Button("Unlock", variant="success", id="unlock-btn")
                yield Button("Retry", variant="primary", id="retry-btn")
                yield Button("Update", variant="success", id="update-btn")
            with Container(id="loading-container"):
                yield LoadingIndicator(id="loading-animation")

    def on_mount(self) -> None:
        self.container = self.query_one("#modal-container")
        self.status_message = self.query_one("PasswordInput #status-message")
        self.config.message=""
        self.enter_error()

    def update_text(self, text: str):
        self.status_message.update(text)

    @on(Input.Submitted, "PasswordInput #password")
    @on(Button.Pressed, "#unlock-btn")
    @on(Button.Pressed, "#update-btn")
    @on(Button.Pressed, "#retry-btn")
    def unlock_button(self) -> None:
        password = self.query_one("PasswordInput").trigger_submit()

        if not password:
            return
        self.query_one("#modal-container").add_class("loading")
        self.status_message.update("[bold blue]Unlocking Vault[/]\n\n\nPlease wait")

        self.call_service(password)
    
    @on(Button.Pressed, "#cancel-btn")
    def cancel_button(self) -> None:
        self.dismiss(None)

    @work
    async def call_service(self, value: str) -> None:
        service_func = self.current_config["service"]
        result = await service_func(value)

        self.query_one("#modal-container").remove_class("loading")

        if result == ResponseStatus.SUCCESS:
            self.dismiss(result)
        else:
            self.config = result
            self.enter_error()

    def enter_error(self):
        self.status_message.update(self.config.message)
        self.query_one("#update-btn").display = self.config.show_update
        self.query_one("#retry-btn").display = self.config.show_retry
        self.query_one("#unlock-btn").display = self.config.show_unlock
        self.query_one("#update-btn").display = self.config.show_update