from textual import on, work
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button
from textual.containers import Container
from custom_widgets import PasswordInput, StateOverlay
from models.status import ResponseStatus



class PasswordModal(ModalScreen[str]):
    """A pop-up modal for user input prompts"""
    
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
        with Container():
            yield StateOverlay()
            # with Horizontal(id="button-container"):
            #     yield Button("Cancel", variant="error", id="cancel-btn")
            #     yield Button("Unlock", variant="success", id="unlock-btn")
            # with Container(id="loading-container"):
            #     yield LoadingIndicator(id="loading-animation")

    def on_mount(self) -> None:
        self.container = self.query_one("#modal-container")
        self.status_message = self.query_one("PasswordInput #status-message")

    def update_text(self, text: str):
        self.status_message.update(text)

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
        service_func = self.current_config["service"]
        result = await service_func(value)
        error_msg=""

        if result in (ResponseStatus.SUCCESS):
            self.dismiss(result)
        elif result == ResponseStatus.WRONG_PASSWORD:
            self.query_one("#modal-container").remove_class("loading")
            error_msg = "[red]Incorrect Master Password[/]"
        elif result == ResponseStatus.TOKEN_INVALID:
            self.query_one("#modal-container").remove_class("loading")
            error_msg = f"[red]Invalid provider Token[/]"
            
        self.status_message.update(error_msg)

        
        

   