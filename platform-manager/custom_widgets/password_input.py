from textual import on
from textual.containers import Horizontal
from textual.widgets import Input, Button, Static
from textual.validation import Length
from textual.app import ComposeResult


class PasswordInput(Static):
    DEFAULT_CSS = """
    #password-wrapper {
        border: tall $accent;
        background: $surface;
        height: 3; 
        width: 100%;
        padding: 0 1;
    }

    #password-wrapper.-invalid {
        border: tall $error;
        color: $error;
    }

    #password-wrapper.-valid {
        border: tall $success;
    }

    #password,
    #password:focus {
        border: none !important;
        width: 1fr;
        height: 1;
        margin: 0;
        padding: 0;
        background: transparent;
    }

    #toggle-eye-btn {
        border: none;
        background: transparent;
        color: $text-muted;
        min-width: 4;
        width: 4;
        height: 1;
        padding: 0;
        margin: 0;
    }

    #toggle-eye-btn:hover {
        color: $accent;
        text-style: bold;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="password-wrapper"):
            yield Input(
                placeholder="Master Password",
                password=True,
                id="password",
                validators=[
                    Length(minimum=1) 
                ]
            )
            yield Button("○", variant="primary", id="toggle-eye-btn")
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Called whenever the user types in the password field."""
        wrapper = self.query_one("#password-wrapper")
        
        if event.validation_result and not event.validation_result.is_valid:
            wrapper.add_class("-invalid")
            wrapper.remove_class("-valid") 
        else:
            wrapper.remove_class("-invalid")
            wrapper.add_class("-valid")
    
    @on(Button.Pressed, "#toggle-eye-btn")
    def toggle_password_visibility(self) -> None:
        pw_input = self.query_one("#password", Input)
        toggle_btn = self.query_one("#toggle-eye-btn", Button)  
        pw_input.password = not pw_input.password
        toggle_btn.label = "○" if pw_input.password else "●"
        pw_input.focus()