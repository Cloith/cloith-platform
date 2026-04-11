from textual.widgets import (
    Static, Button
)
from textual.containers import VerticalScroll
from textual.app import ComposeResult

class ProviderView(Static):
    DEFAULT_CSS = """
    ProviderView {
        align: center middle;
        width: 100%;
        height: 1fr;
    }

    #button-stack {
        width: 1fr;           
        height: 15;
        background: $boost;
        align: center middle;
        border: hkey $success;
    }

    #button-stack Button {
        width: 100%; 
        height: 3;       
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="button-stack"):
            yield Button("Hostinger", id="hostinger-btn", variant="primary")
            yield Button("AWS", id="aws-btn")
            yield Button("GCP", id="gcp-btn")
            yield Button("Azure", id="azure-btn")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "hostinger-btn":
            self.app.notify("hostinger")
        else:
            self.app.notify("Coming Soon!")