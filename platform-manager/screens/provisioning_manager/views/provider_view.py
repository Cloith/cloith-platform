from textual import on
from textual.widgets import (
    Static, Button
)
from textual.containers import VerticalScroll
from textual.app import ComposeResult

class ProviderView(Static):
    CSS_PATH = "tcss/provider_view.tcss"

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="button-stack"):
            yield Button("Hostinger", id="hostinger-button", variant="primary")
            yield Button("AWS", id="aws-button")
            yield Button("GCP", id="gcp-button")
            yield Button("Azure", id="azure-button")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "hostinger-button":
            self.app.notify("hostinger")