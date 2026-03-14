from textual import on
from textual.app import ComposeResult
from textual.widgets import Static, Input, Button, LoadingIndicator
from textual.containers import Vertical, Container
from textual.validation import Integer, Function
from screens.dashboard_screen import DashboardScreen
from screens.base_screen import AppScreen
from services.base_vault import BaseVaultService, AuthStatus
from custom_widgets.password_input import PasswordInput
from services.service_factory import get_vault_service


class LoginScreen(AppScreen):
    """A secure login screen for the Platform Manager."""
    CSS_PATH = "login_screen.tcss"
    
    def __init__(self, vault_service: BaseVaultService):
        super().__init__()
        self.vault_service = vault_service
    
    def setup_content(self) -> ComposeResult:
        with Vertical(id="main-container"):
            yield Static("BITWARDEN LOGIN REQUIRED", id="login-title")
            with Vertical(id="login-container"):
                yield Input(
                    placeholder="Email Address",
                    id="email",
                    validators=[
                        Function(lambda s: "@" in s and "." in s, "Invalid email format")
                    ]
                )
                yield PasswordInput()
            with Container(id="otp-container"):
                yield Input(
                    placeholder="Enter 2FA / OTP Code",
                    id="otp",
                    validators=[
                        Integer()  
                    ]
                )
            with Container(id="button-container"):
                yield LoadingIndicator()
                yield Button("Login", variant="primary", id="login-btn")
                yield Button("Enter OTP", variant="primary", id="otp-btn")
            with Container(id="status-message-container"):
                yield Static("", id="status-message")

    def on_mount(self) -> None:
        self.status_text = self.query_one("#status-message")
        self.main_container = self.query_one("#main-container", Vertical)
        
    @on(Input.Submitted, "#email")
    @on(Input.Submitted, "#password")
    @on(Button.Pressed, "#login-btn")
    def on_button_pressed(self) -> None:
        """Called when the user clicks the Login button."""
        email = self.query_one("#email", Input).value
        if not email:
            self.status_text.update("[bold red]Email field must not be empty.[/bold red]")
            return
        if "@" not in email or "." not in email:
            self.status_text.update("[bold red]Please enter a valid email.[/bold red]")
            return
        
        password = self.query_one("#password", Input).value
        if not password:
            self.status_text.update("[bold red]Password field must not be empty[/bold red]")
            return

        self.query_one("#button-container").add_class("searching")
        self.status_text.update("[bold yellow]Validating Credentials...[/bold yellow]")

        self.vault_service.run_login_thread(email, password, self.ask_otp, self.handle_login_result)

    def ask_otp(self):
        """Safe UI transformation (called via call_from_thread)"""
        self.main_container.add_class("ask-otp")
        self.status_text.update("[bold cyan]Two-Step Verification Required[/bold cyan]")
        self.query_one("#otp").value = ""
        self.query_one("#button-container").remove_class("searching")
    
    @on(Input.Submitted, "#otp")
    @on(Button.Pressed, "#otp-btn")
    async def handle_otp_submission(self):
        otp = self.query_one("#otp", Input).value
        if not otp:
            self.status_text.update("[bold red]OTP field must not be empty.[/bold red]")
            return

        if not otp.isdigit():
            self.status_text.update("[bold red]OTP must only contain numbers.[/bold red]")
            return
           
        self.status_text.update("[bold yellow]Validating OTP...[/bold yellow]")
        self.query_one("#button-container").add_class("searching")

        self.app.otp_code = otp
        self.vault_service._otp_event.set()

    def handle_login_result(self, result: tuple[int, str | None]):
        """This runs on the MAIN THREAD automatically via call_from_thread"""
        status_code, session_key = result
        self.query_one("#button-container").remove_class("searching")
        
        if status_code == AuthStatus.SUCCESS:
            self.app.bw_session = session_key
            self.notify(f"{self.app.bw_session}")
            vault_service = get_vault_service("bitwarden", self.app)
            self.app.push_screen(DashboardScreen(vault_service))
        elif status_code == AuthStatus.WRONG_PASSWORD:
            self.status_text.update("[bold red]Incorrect Email or Password[/bold red]")
        elif status_code == AuthStatus.INVALID_OTP:
            self.reset_ui_to_login()
            self.query_one("#status-message").update("[bold red]Incorrect OTP[/bold red]")
        
    def reset_ui_to_login(self):
        """Restores the UI from OTP mode back to standard Login mode."""
        self.main_container.remove_class("ask-otp")
        self.query_one("#button-container").remove_class("searching")
        password_input = self.query_one("#password", Input)
        password_input.value = ""
        