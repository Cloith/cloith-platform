from textual import on, work
from textual.widgets import (
    Static, Input, Button, 
)
from textual.containers import Vertical, Horizontal, Container
from textual.app import ComposeResult
from models.password import PasswordPolicy, PANEL_PASSWORD_POLICY, VPS_PASSWORD_POLICY
from custom_widgets.rich_spinner import LoadingSpinner
from custom_widgets.password_input import PasswordInput
from screens import BaseScreen
from screens.components.common.password_requirements import PasswordRequirementList


class PolicyPasswordForm(Static):
    def __init__(self, policy: PasswordPolicy):
        super().__init__()
        self.policy = policy
        # self.leak_symbol = "[b red]✖[/]"   
        # self.leak_message = " Password must not be leaked publicly"
        
    
    def compose(self)-> ComposeResult:
        if self.policy == PANEL_PASSWORD_POLICY:
            placeholder = "ENTER PANEL PASSWORD"
        else:
            placeholder = "ENTER VPS PASSWORD"
        yield PasswordInput(placeholder=placeholder)
        yield PasswordRequirementList(self.policy, id="requirements-list")
        # yield Static(f"{self.leak_symbol} {self.leak_message}", id="leak-message")
        # with Horizontal(id="leak-animation-container"):
        #     with Container(id="leak-animation"):
        #         yield LoadingSpinner("clock")
        #     yield Static("Checking if leaked")
        with Horizontal(id="enter-button-container"):
            yield Button.success("ENTER", id="enter-button")
    
    def on_mount(self):
        self.req_update = self.query_one("#requirements-list", PasswordRequirementList)

    @on(Input.Changed, "PasswordInput #password")
    async def validate_password(self, event: Input.Changed) -> None:
        pw = event.value
        self.req_update.update_requirements_widgets(pw=pw)

    # @on(Input.Changed, "#password")
    # async def validate_password(self, event: Input.Changed) -> None:
    #     pw = event.value
    #     self.current_password = pw

    #     checks = self.password_service.validate_rules(pw)

    #     self.update_requirements_widgets(checks)

    #     if self.password_service.policy.check_leak and all(checks.values()):
    #         self.password_container.add_class("show-animation")
    #         self.password_container.remove_class("check-for-leak")
    #         self.run_leak_check(pw)
    #     else:
    #         self.password_container.remove_class("show-animation")
    #         self.password_container.add_class("check-for-leak")
    #         self.leak_symbol = "[b red]✖[/]"   
    #         self.leak_message = " Password must not be leaked publicly"
    #         self.leak_widget.update(f"{self.leak_symbol} {self.leak_message}")


    # def update_requirements_widgets(self, checks: dict[str, bool]) -> None:
    #     """Refreshes the UI icons and colors based on validation results."""
    #     for req_id, is_valid in checks.items():
    #         try:
    #             widget = self.query_one(f"#{req_id}", Static)
                
    #             req_data = next(
    #                 item for item in self.policy.get_requirements_data() 
    #                 if item["id"] == req_id
    #             )
    #             original_text = req_data["text"]

    #             symbol = "[b green]✔[/]" if is_valid else "[b red]✖[/]"
    #             widget.update(f"{symbol} {original_text}")

    #             widget.set_class(is_valid, "req-valid")
    #             widget.set_class(not is_valid, "req-invalid")
                
    #         except Exception:
    #             continue
    
    # @work(thread=True)
    # async def run_leak_check(self, password: str) -> None:
    #     """Background worker to check for leaks without freezing the UI."""
    #     if password != self.current_password:
    #         return
    #     is_leaked = await self.password_service.is_password_leaked(password)

    #     if is_leaked:
    #         self.leak_symbol = "[b red]✖[/]"
    #         self.leak_message = "This password was found in a data breach!"
    #         self.leak_widget.set_class(False, "req-valid")
    #     else:
    #         self.leak_symbol = "[b green]✔[/]"
    #         self.leak_message = "This password is safe (not leaked)."
    #         self.leak_widget.set_class(True, "req-valid")

    #     self.leak_widget.update(f"{self.leak_symbol} {self.leak_message}")

    #     self.password_container.remove_class("show-animation")
    #     self.password_container.add_class("check-for-leak")