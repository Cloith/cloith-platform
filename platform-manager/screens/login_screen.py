import threading
from textual import work, on
from textual.worker import Worker
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Static, Input, Button, LoadingIndicator
from textual.containers import Vertical, Horizontal
from textual.validation import Integer, Function, Length
from screens.dashborad_screen import DashboardScreen
from providers.bitwarden import login_to_bitwarden

class LoginScreen(Screen):
    """A secure login screen for the Platform Manager."""
    CSS_PATH = "login_screen.tcss"
    
    def __init__(self):
        super().__init__()
        self.otp_event = threading.Event()
        self.entered_otp = ""             
    
    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="login-container"):
            yield Static("BITWARDEN LOGIN REQUIRED", id="login-title")
            
            yield Input(
                placeholder="Email Address",
                id="email",
                validators=[
                    Function(lambda s: "@" in s and "." in s, "Invalid email format")
                ]
            )
            with Horizontal(id="password-wrapper"):
                yield Input(
                    placeholder="Master Password",
                    password=True,
                    id="password",
                    validators=[
                        Length(minimum=1) 
                    ]
                )
                yield Button("○", variant="primary", id="toggle-pw-btn")
            yield Input(
                placeholder="Enter 2FA / OTP Code",
                id="otp",
                validators=[
                    Integer()  
                ]
            )
            
            with Vertical(id="button-container"):
                yield LoadingIndicator()
                yield Button("Login", variant="primary", id="login-btn")
                yield Button("Enter OTP", variant="primary", id="otp-btn")
            
            yield Static("", id="status-message")

    def get_otp_from_ui(self):
        self.app.call_from_thread(self.ask_otp_ui)

        self.otp_event.wait() 
        self.otp_event.clear() 
        return self.entered_otp
    
    def ask_otp_ui(self):
        """Safe UI transformation (called via call_from_thread)"""
        self.query_one("#otp").value = ""
        self.query_one("#button-container").remove_class("searching")
        self.query_one("#status-message").update("[bold cyan]Two-Step Verification Required[/bold cyan]")
        self.query_one("#login-container").add_class("otp")

    @work(thread=True)
    def perform_login_task(self, email, password):
        return login_to_bitwarden(email, password, self.get_otp_from_ui)
    
    @on(Input.Submitted, "#otp")
    @on(Button.Pressed, "#otp-btn")
    def handle_otp_submission(self):
        otp = self.query_one("#otp", Input).value
        if not otp:
            self.query_one("#status-message").update("[bold red]OTP field must not be empty.[/bold red]")
            return

        if not otp.isdigit():
            self.query_one("#status-message").update("[bold red]OTP must only contain numbers.[/bold red]")
            return
        
        self.entered_otp = otp
        self.otp_event.set()
        
        self.query_one("#status-message").update("[bold yellow]Validating OTP...[/bold yellow]")
        self.query_one("#button-container").add_class("searching")
    
    @on(Input.Submitted, "#email")
    @on(Input.Submitted, "#password")
    @on(Button.Pressed, "#login-btn")
    def on_button_pressed(self) -> None:
        """Called when the user clicks the Login button."""
        email = self.query_one("#email", Input).value
        if not email:
            self.query_one("#status-message").update("[bold red]Email field must not be empty.[/bold red]")
            return
        if "@" not in email or "." not in email:
            self.query_one("#status-message").update("[bold red]Please enter a valid email.[/bold red]")
            return
        
        password = self.query_one("#password", Input).value
        if not password:
            self.query_one("#status-message").update("[bold red]Password field must not be empty[/bold red]")
            return

        self.query_one("#button-container").add_class("searching")
        self.query_one("#status-message").update("[bold yellow]Validating Credentials...[/bold yellow]")
        self.perform_login_task(email, password)

    @on(Button.Pressed, "#toggle-pw-btn")
    def toggle_password_visibility(self) -> None:
        pw_input = self.query_one("#password", Input)
        toggle_btn = self.query_one("#toggle-pw-btn", Button)      
        pw_input.password = not pw_input.password
        toggle_btn.label = "○" if pw_input.password else "●"
        pw_input.focus()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called automatically when the background login finishes."""
        if event.worker.is_finished:
            #self.query_one("#button-container").remove_class("searching")
            status = self.query_one("#status-message", Static)
            try:
                code, key = event.worker.result
                
                if code == 1:
                    self.app.bw_session = key
                    self.app.push_screen(DashboardScreen())
                elif code == 3:
                    status.update(f"[bold red]Incorrect Password[/bold red]")
                    self.query_one("#login-container").remove_class("searching")
                    self.reset_ui_to_login()
                elif code == 4:
                    status.update(f"[bold red]Incorrect Email[/bold red]")
                    self.query_one("#login-container").remove_class("searching")
                    self.reset_ui_to_login()
                elif code == 5:
                    status.update(f"[bold red]Invalid OTP[/bold red]")
                    self.query_one("#login-container").remove_class("otp")
                    self.reset_ui_to_login()
                else:
                    self.query_one("#button-container").remove_class("searching")
                    status.update(f"[bold red]Invalid Credentials. Please try again.[/bold red]")
            except Exception as e:
                self.query_one("#button-container").remove_class("searching")
                self.query_one("#status-message").update("[bold red]Connection Error.[/bold red]")
                self.reset_ui_to_login()

    def reset_ui_to_login(self):
        """Restores the UI from OTP mode back to standard Login mode."""
        self.query_one("#login-container").remove_class("otp")
        self.query_one("#button-container").remove_class("searching")
        password_input = self.query_one("#password", Input)
        password_input.value = ""
        
    def on_unmount(self) -> None:
        self.workers.cancel_all()

    


        
        

    


  
              