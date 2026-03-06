from textual import on, work
from textual.widgets import (
    Static, Input, Button, 
)
from textual.containers import Vertical, Horizontal, Container
from textual.app import ComposeResult
from services.password_service import PasswordService
from services.password_policy import PasswordPolicy
from widgets.rich_spinner import LoadingSpinner


class PolicyPasswordTab(Static):
    def __init__(self, policy: PasswordPolicy):
        super().__init__()
        self.policy = policy
        self.password_service = PasswordService(policy)
        self.leak_symbol = "[b red]✖[/]"   
        self.leak_message = " Password must not be leaked publicly"
        
    
    def compose(self)-> ComposeResult:
        with Horizontal(id="password-wrapper"):
            yield Input(placeholder="Enter Password", password=True, id="panel-password-input")
            yield Button("○", variant="primary", id="toggle-pw-btn")
        with Vertical(id="password-requirements"):
            for req in self.policy.get_requirements_data():
                yield Static(
                    f"[b red]✖[/] {req['text']}", 
                    id=req['id'], 
                    classes="req-invalid"
                )
            yield Static(f"{self.leak_symbol} {self.leak_message}", id="leak-message")
            with Horizontal(id="leak-animation-container"):
                with Container(id="leak-animation"):
                    yield LoadingSpinner("clock")
                yield Static("Checking if leaked")
        with Horizontal(id="enter-button-container"):
            yield Button.success("ENTER", id="enter-button")

    def on_mount(self) -> None:
        self.password_container = self.query_one("#password-requirements")
        self.leak_widget = self.query_one("#leak-message", Static)
        if self.policy.check_leak:
            self.query_one("#password-requirements").add_class("check-for-leak")

    @on(Button.Pressed, "#toggle-pw-btn")
    def toggle_password_visibility(self) -> None:
        pw_input = self.query_one("#panel-password-input", Input)
        toggle_btn = self.query_one("#toggle-pw-btn", Button)  
        pw_input.password = not pw_input.password
        toggle_btn.label = "○" if pw_input.password else "●"
        pw_input.focus()

    @on(Input.Changed, "#panel-password-input")
    async def validate_password(self, event: Input.Changed) -> None:
        pw = event.value
        self.current_password = pw

        checks = self.password_service.validate_rules(pw)

        self.update_requirements_widgets(checks)

        if self.password_service.policy.check_leak and all(checks.values()):
            self.password_container.add_class("show-animation")
            self.password_container.remove_class("check-for-leak")
            self.run_leak_check(pw)
        else:
            self.password_container.remove_class("show-animation")
            self.password_container.add_class("check-for-leak")
            self.leak_symbol = "[b red]✖[/]"   
            self.leak_message = " Password must not be leaked publicly"
            self.leak_widget.update(f"{self.leak_symbol} {self.leak_message}")


    def update_requirements_widgets(self, checks: dict[str, bool]) -> None:
        """Refreshes the UI icons and colors based on validation results."""
        for req_id, is_valid in checks.items():
            try:
                widget = self.query_one(f"#{req_id}", Static)
                
                req_data = next(
                    item for item in self.policy.get_requirements_data() 
                    if item["id"] == req_id
                )
                original_text = req_data["text"]

                symbol = "[b green]✔[/]" if is_valid else "[b red]✖[/]"
                widget.update(f"{symbol} {original_text}")

                widget.set_class(is_valid, "req-valid")
                widget.set_class(not is_valid, "req-invalid")
                
            except Exception:
                continue

    @work(exclusive=True)
    async def run_leak_check(self, password: str) -> None:
        """Background worker to check for leaks without freezing the UI."""
        if password != self.current_password:
            return
        # 1. Perform the API call
        is_leaked = await self.password_service.is_password_leaked(password)


        # 3. Update the state and THE UI
        if is_leaked:
            self.leak_symbol = "[b red]✖[/]"
            self.leak_message = "This password was found in a data breach!"
            self.leak_widget.set_class(False, "req-valid") # Ensure it looks red
        else:
            self.leak_symbol = "[b green]✔[/]"
            self.leak_message = "This password is safe (not leaked)."
            self.leak_widget.set_class(True, "req-valid") # Ensure it looks green

        # 4. CRITICAL: Push the update to the widget
        self.leak_widget.update(f"{self.leak_symbol} {self.leak_message}")

        # 5. Clean up the classes to show the message again
        self.password_container.remove_class("show-animation")
        self.password_container.add_class("check-for-leak")

                
     