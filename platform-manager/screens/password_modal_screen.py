from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Button, Static
from textual.containers import Container, Horizontal
from custom_widgets.password_input import PasswordInput

class PasswordModal(ModalScreen[str]):
    """A pop-up modal to capture the Master Password."""
    
    DEFAULT_CSS = """
    PasswordModal {
        align: center middle;
    }

    #modal-container {
        width: 50;
        height: auto;
        border: round $accent;
        background: $surface;
        padding: 1 2;
        align: center middle;
    }

    #button-container {
        align: center middle;
    }

    Label {
        width: 100%;
        content-align: center middle;
        margin-bottom: 1;
    }
    """

    def __init__(self, message: str = "Input Master Password to Continue"):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(self.message)
            yield PasswordInput()
            with Horizontal(id="button-container"):
                yield Button("Cancel", variant="error", id="cancel")
                yield Button("Unlock", variant="success", id="unlock")
                
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "unlock":
            password = self.query_one("#password", Input).value
            self.dismiss(password)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)