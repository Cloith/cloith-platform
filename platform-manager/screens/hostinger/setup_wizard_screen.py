from textual import on
from textual.widgets import (
    Static, RadioButton, Button
)
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.app import ComposeResult
from screens.base_screen import AppScreen
from screens.hostinger.provisioning.provisioning_screen import ProvisioningScreen
from services.textual_message_bus import DescriptionUpdate


class SetupWizardScreen(AppScreen):
    CSS_PATH = "setup_wizard_screen.tcss"

    def __init__(self, selected_vps: dict):
        super().__init__()

    def setup_content(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            with Vertical(id="selection-panel"):
                yield Static("[b]Setup Wizard[/b]", id="title")
                with Container(id="panels"):
                    yield VerticalScroll(
                        Button("Provisioning(required)", id="provisioning-button", classes="selection-buttons"),
                        Button("Networking", id="networking-button", classes="selection-buttons"),
                        Button("Hardening", id="hardening-button", classes="selection-buttons"),
                        Button("Custom Playbooks", id="custom-button", classes="selection-buttons"),
                        Button("Requirements", id="requirements-button", classes="selection-buttons"),
                        Button("Review", id="review-button", classes="selection-buttons"),
                        Button("Deploy", id="deploy-button", classes="selection-buttons"),
                    )
                with VerticalScroll(id="description-panel"):
                    yield Static("", id="description-text")
            with Container(id="forms-panel"):
                yield Container(ProvisioningScreen())
                with Container(id="description-button-container"):
                    yield RadioButton("Details", id="description-button")
                    
    def on_mount(self) -> None:
        self.query_one("#description-panel").display=False

    @on(RadioButton.Changed, "#description-button")
    def description_button(self) -> None:
        self.container1 = self.query_one("#panels")
        self.container2 = self.query_one("#description-panel")

        self.container1.toggle_class("hide-contents")

        if self.container1.has_class("hide-contents"):
            self.container1.display = False
            self.container2.display = True
        else:
            self.container1.display = True
            self.container2.display = False

    def on_description_update(self, message: DescriptionUpdate) -> None:
        """This handler catches the message from the deep child."""
        self.query_one("#description-text", Static).update(message.text)