from textual.app import ComposeResult
from textual.widgets import Static, Header, Footer
from textual.screen import Screen
from textual.containers import Container

class AppScreen(Screen):
    """The base screen for the entire app. Sets global layout constraints."""
    
    # We define the CSS for the base class here
    DEFAULT_CSS = """
    AppScreen {
        align: center middle;
        background: $background;
    }

    #app-canvas {
        max-width: 134;
        max-height: 17;
        background: $boost;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-canvas"):
            yield from self.setup_content()
        yield Footer()
  

    def setup_content(self) -> ComposeResult:
        """Placeholder for child screens to override"""
        yield Static("Default Content")
