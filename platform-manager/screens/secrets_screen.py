from textual.app import ComposeResult
from textual.widgets import Static, Header
from textual.screen import Screen

#CSS_PATH = "secrets_screen.tcss"

class SecretsScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Hello")