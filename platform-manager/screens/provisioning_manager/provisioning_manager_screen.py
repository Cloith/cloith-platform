from textual import on
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static, RadioButton, Button, Markdown
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from screens import BaseScreen
from .views import ProviderView, ProvisioningView, ImportView
from services.textual_message_bus import DescriptionUpdate
from custom_widgets.sidebar import NavigationSidebar
from models.deployment_recipe import DeploymentRecipe
from custom_widgets.state_overlay import StateOverlay

class ProvisioningManagerScreen(BaseScreen):
    CSS_PATH = [
        "tcss/provisioning_manager_screen.tcss"
        ]
    

    def setup_content(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            yield NavigationSidebar()
            with Vertical(id="selection-panel"):
                yield Static("[b]Provisioning Manager[/b]", id="title")
                with Horizontal(id="initial-options"):
                    yield Button("Select Provider", id = "provider-btn", classes = "initial-btn")
                    yield Button("Import Template", id = "import-btn", classes = "initial-btn")
                with Container(id="panels"):
                    yield StateOverlay(id="status-overlay")
                    yield VerticalScroll(
                        Button("VPS Selection", id="vps-button", classes="selection-buttons"),
                        Button("Provisioning(required)", id="provisioning-button", classes="selection-buttons"),
                        Button("Requirements", id="requirements-button", classes="selection-buttons"),
                        Button("Deploy", id="deploy-button", classes="selection-buttons"),
                        id = "panel-scroll"
                    )
                with VerticalScroll(id="description-panel"):
                    yield Markdown("", id="description-text")
            with Vertical(id="forms-panel"):
                yield Static("SELECT YOUR PROVIDER", id="view-title")
                with Container(id="active-form-container"): 
                    yield ProviderView()
                with Container(id="description-button-container"):
                    yield RadioButton("Details", id="description-button")
        
                    
    def on_mount(self) -> None:
        self.query_one("#description-panel").display=False
        self.view_title = self.query_one("#view-title")
        self.overlay = self.query_one("#status-overlay")
        message = """[orange]No Provider detected[/] \n\n Choose a [yellow bold]Provider or Import[/] first to get started"""
        self.overlay.enter_error(message, show_retry = False, show_auth = False)

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
        self.query_one("#description-text").update(message.text)

    @on(Button.Pressed)
    def handle_menu_navigation(self, event: Button.Pressed) -> None:
        """Main router for the sidebar buttons."""
        button_id = event.button.id

        if button_id == "provider-btn":
            self.switch_view(ProviderView())
            self.view_title.update("SELECT YOUR PROVIDER")

        elif button_id == "import-btn":
            self.switch_view(ImportView())
            self.view_title.update("CHOOSE YOUR TEMPLATE")   
            
        elif button_id == "provisioning-button":
            self.switch_view(ProvisioningView())
            self.view_title.update("COMPLETE THE FORMS")   
            
    def switch_view(self, new_view: Static) -> None:
        """Removes the current form and mounts a new one."""
        container = self.query_one("#active-form-container")
        
        for child in container.children:
            child.remove()
            
        container.mount(new_view)

    recipe = reactive(DeploymentRecipe())

    def watch_recipe(self, old_recipe: DeploymentRecipe, new_recipe: DeploymentRecipe) -> None:
        """This runs whenever the recipe object is swapped or updated."""
        self.update_ui_state()

    def update_ui_state(self) -> None:
        """Central logic to enable/disable panels based on the recipe."""
        has_source = self.recipe.has_provider
        
        self.overlay.display = not has_source
        
        self.query_one("#panels").disabled = not has_source
        
        if has_source:
            self.view_title.update(f"CONFIGURING: [bold]{self.recipe.provider.upper()}[/]")