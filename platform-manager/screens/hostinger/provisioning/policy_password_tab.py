from textual import on, work
from textual.widgets import (
    Static, Input, Button, 
)
from textual.containers import Vertical, Horizontal, Container
from textual.app import ComposeResult
from services.password_service import PasswordService
from models.password import PasswordPolicy
from custom_widgets.rich_spinner import LoadingSpinner
from custom_widgets.password_input import PasswordInput


class PolicyPasswordTab(Static):
    def __init__(self, policy: PasswordPolicy):
        super().__init__()
        self.policy = policy
        self.password_service = PasswordService(policy)
        self.leak_symbol = "[b red]✖[/]"   
        self.leak_message = " Password must not be leaked publicly"
        
    
    def compose(self)-> ComposeResult:
        yield PasswordInput()
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
        is_leaked = await self.password_service.is_password_leaked(password)

        if is_leaked:
            self.leak_symbol = "[b red]✖[/]"
            self.leak_message = "This password was found in a data breach!"
            self.leak_widget.set_class(False, "req-valid")
        else:
            self.leak_symbol = "[b green]✔[/]"
            self.leak_message = "This password is safe (not leaked)."
            self.leak_widget.set_class(True, "req-valid")

        self.leak_widget.update(f"{self.leak_symbol} {self.leak_message}")

        self.password_container.remove_class("show-animation")
        self.password_container.add_class("check-for-leak")