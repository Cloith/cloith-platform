from textual import work
from textual.widgets import Static, LoadingIndicator, Button
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from screens.common import PasswordModal
from models import ResponseStatus, ConfigClass
from services.textual_message_bus import GlobalRetryRequested

class StateOverlay(Vertical):
    """A reusable overlay for Loading, Error, and Auth states."""
    
    DEFAULT_CSS = """
    StateOverlay {
        width: 100%;
        height: 100%;
        align: center middle;
        display: none;
    }
    StateOverlay.-visible { display: block; }
    #overlay-text { text-align: center; margin-bottom: 1; }
    #overlay-buttons { align: center middle; height: 5; display: none; }
    #overlay-indicator { height: 6; }
    StateOverlay.-show-buttons #overlay-buttons { display: block; }
    .buttons {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="overlay-indicator")
        yield Static("", id="overlay-text")
        with Horizontal(id="overlay-buttons"):
            yield Button("Try Again", variant="primary", id="retry-btn", classes="buttons")
            yield Button("Authorize", variant="primary", id="auth-btn", classes="buttons")
            yield Button("Buy VPS", variant="success", id="buy-btn", classes="buttons")
            yield Button("Update Token", variant="success", id="update-btn", classes="buttons")



    def enter_loading(self, message: str):
        """displays a loading animation with the inputed text below it"""
        self.add_class("-visible")
        self.remove_class("-show-buttons")
        self.query_one("#overlay-indicator").display = True
        self.query_one("#overlay-text").update(message)

    def hide_loading(self):
        """hides the loading animation""" 
        self.remove_class("-visible")
        self.remove_class("-show-buttons")
        
    def enter_error(self, config: ConfigClass):
        self.mode = config.mode
        self.config = config
        self.add_class("-visible", "-show-buttons")
        self.query_one("#overlay-indicator").display = False
        self.query_one("#overlay-text").update(config.message)
        self.query_one("#retry-btn").display = config.show_retry
        self.query_one("#auth-btn").display = config.show_auth
        self.query_one("#buy-btn").display = config.show_buy
        self.query_one("#update-btn").display = config.show_update

    def clear(self):
        self.remove_class("-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "retry-btn":
            self.global_message_sender()
        elif event.button.id in ("auth-btn", "update-btn"):
            self.handle_authorization()
        elif event.button.id == "buy-btn":
            self.app.notify("Coming Soon!")
    
    @work
    async def handle_authorization(self):
        """
        Handles the modal password prompt and triggers a global refresh 
        across all app screens upon successful authentication.
        """
        result = await self.app.push_screen_wait(PasswordModal(self.mode, self.config))

        if result == ResponseStatus.SUCCESS:
            self.global_message_sender()

    def global_message_sender(self):
        """
        Iterates through the current screen stack and broadcasts a 
        GlobalRetryRequested message to all active screens.

        This ensures that background screens (like the Provisioning Manager or Dashboard)
        wake up and refresh their data once the vault is unlocked, without
        requiring the user to manually click 'Retry' on every tab.
        
        It explicitly skips the PasswordModal to avoid sending refresh 
        requests to a screen that is in the process of closing.
        """
        for screen in self.app.screen_stack:
            if screen.__class__.__name__ != "PasswordModal":
                screen.post_message(GlobalRetryRequested())