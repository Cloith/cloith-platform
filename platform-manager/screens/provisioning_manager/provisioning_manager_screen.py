from textual import on
from textual.widgets import Static, RadioButton, Button
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.app import ComposeResult
from screens import BaseScreen
from .views import ProviderView, ProvisioningView
from services.textual_message_bus import DescriptionUpdate

class ProvisioningManagerScreen(BaseScreen):
    CSS_PATH = [
        "tcss/provisioning_manager_screen.tcss",
        "views/tcss/provider_view.tcss"
        ]

    def setup_content(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            with Vertical(id="selection-panel"):
                yield Static("[b]Provisioning Manager[/b]", id="title")
                with Container(id="panels"):
                    yield VerticalScroll(
                        Button("Select Provider", id="provider-button", classes="selection-buttons"),
                        Button("VPS Selection", id="vps-button", classes="selection-buttons"),
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
            with Vertical(id="forms-panel"):
                yield Static("SELECT YOUR PROVIDER", id="view-title")
                with Container(id="active-form-container"): 
                    yield ProviderView()
                with Container(id="description-button-container"):
                    yield RadioButton("Details", id="description-button")
                    
    def on_mount(self) -> None:
        self.query_one("#description-panel").display=False
        self.view_title = self.query_one("#view-title")

    @on(RadioButton.Changed, "#description-button")
    def description_button(self) -> None:
        self.container1 = self.query_one("#panels")
        self.container2 = self.query_one("#description-panel")

        self.container1.toggle_class("reveal-details")

        if self.container1.has_class("reveal-details"):
            self.container1.display = False
            self.container2.display = True
        else:
            self.container1.display = True
            self.container2.display = False

    def on_description_update(self, message: DescriptionUpdate) -> None:
        """This handler catches the message from the deep child."""
        self.query_one("#description-text", Static).update(message.text)

    @on(Button.Pressed)
    def handle_menu_navigation(self, event: Button.Pressed) -> None:
        """Main router for the sidebar buttons."""
        button_id = event.button.id

        if button_id == "provider-button":
            self.switch_view(ProviderView())
            self.view_title.update("SELECT YOUR PROVIDER")
            
        elif button_id == "provisioning-button":
            self.switch_view(ProvisioningView()) 
            
        elif button_id == "networking-button":
            # self.switch_view(NetworkingView())
            self.app.notify("Networking coming soon...")

        elif button_id == "hardening-button":
            # self.switch_view(HardeningView())
            self.app.notify("Hardening coming soon...")

        elif button_id == "custom-button":
            # self.switch_view(HardeningView())
            self.app.notify("Custom Playbooks coming soon...")
        
        elif button_id == "hardening-button":
            # self.switch_view(HardeningView())
            self.app.notify("Hardening coming soon...")


    def switch_view(self, new_view: Static) -> None:
        """Removes the current form and mounts a new one."""
        container = self.query_one("#active-form-container")
        
        for child in container.children:
            child.remove()
            
        container.mount(new_view)