from textual import work
from textual.widgets import Static, LoadingIndicator, Button
from textual.containers import Vertical, Container
from textual.app import ComposeResult
from textual.message import Message
from screens.modal_screen import PasswordModal
from services.base_vault import VaultStatus

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
    #overlay-buttons { align: center middle; height: 3; display: none; }
    #overlay-indicator { height: 6; }
    StateOverlay.-show-buttons #overlay-buttons { display: block; }
    """

    class RetryRequested(Message):
        """Sent when 'Try Again' is pressed."""
        pass

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="overlay-indicator")
        yield Static("", id="overlay-text")
        with Container(id="overlay-buttons"):
            yield Button("Try Again", variant="primary", id="retry-btn")
            yield Button("Authorize", variant="primary", id="auth-btn")

    def enter_loading(self, message: str = "Fetching Data..."):
        self.add_class("-visible")
        self.remove_class("-show-buttons")
        self.query_one("#overlay-indicator").display = True
        self.query_one("#overlay-text").update(message)

    def enter_error(self, message: str, show_retry: bool, show_auth: bool):
        self.add_class("-visible", "-show-buttons")
        self.query_one("#overlay-indicator").display = False
        self.query_one("#overlay-text").update(message)
        self.query_one("#retry-btn").display = show_retry
        self.query_one("#auth-btn").display = show_auth

    def clear(self):
        self.remove_class("-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "retry-btn":
            self.post_message(self.RetryRequested())
        elif event.button.id == "auth-btn":
            self.handle_authorization()
    
    @work
    async def handle_authorization(self):
        result = await self.app.push_screen_wait(PasswordModal())

        if result == VaultStatus.SUCCESS:
            self.post_message(self.RetryRequested())