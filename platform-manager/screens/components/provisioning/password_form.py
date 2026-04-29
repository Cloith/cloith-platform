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
    
    def compose(self)-> ComposeResult:
        if self.policy == PANEL_PASSWORD_POLICY:
            placeholder = "ENTER PANEL PASSWORD"
        else:
            placeholder = "ENTER VPS PASSWORD"
        yield PasswordInput(placeholder=placeholder, id=f"{self.policy.name}_password_input")
        yield PasswordRequirementList(self.policy, id=f"{self.policy.name}_requirements")
        with Horizontal(id="enter-button-container"):
            yield Button.success("ENTER", id="enter-button")
    
    def on_mount(self):
        self.req_update = self.query_one(f"#{self.policy.name}_requirements", PasswordRequirementList)

    @on(Input.Changed, "PasswordInput #password")
    async def validate_password(self, event: Input.Changed) -> None:
        pw = event.value
        self.req_update.update_requirements_widgets(pw=pw)