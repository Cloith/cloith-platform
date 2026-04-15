from textual.app import ComposeResult
from textual.widgets import Static, Header, Footer
from textual.screen import Screen
from textual.containers import Container

class BaseScreen(Screen):
    """The base screen for the entire app. Sets global layout constraints."""
    
    # We define the CSS for the base class here
    CSS = """
    AppScreen {
        align: center middle;
        background: $background;
    }

    #app-canvas {
        max-width: 100%;
        max-height: 100%;
        background: $boost;
        content-align: center middle;
        
    }

    Header {
        dock: top;
    }

    Footer {
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="app-canvas"):
            yield Header()
            yield from self.setup_content()
            yield Footer()
  

    def setup_content(self) -> ComposeResult:
        """Placeholder for child screens to override"""
        yield Static("Default Content")
