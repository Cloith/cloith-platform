from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Static, Button, OptionList
from textual.containers import Vertical, Horizontal
from screens.template_deployment_screen import TemplateDeploymentScreen
from screens.manual_deployment_screen import ProviderSelectionScreen

CSS_PATH = "tcss/deployment_screen.tcss"

class DeploymentScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="deploy-container"):
            yield Static("CHOOSE DEPLOYMENT METHOD", id="deploy-title")
            
            with Horizontal(id="method-selector"):
                yield Button("Template Deployment", variant="primary", id="btn-template")
                yield Button("Manual Configuration", variant="default", id="btn-manual")
                yield Button("Back", variant="default", id="btn-back") 
            
            yield Static(id="coming-soon", classes="hidden")
        yield Footer()

    @on(Button.Pressed, "#btn-manual")
    def manual_button(self) -> None:
        self.app.push_screen(ProviderSelectionScreen())

    @on(Button.Pressed, "#btn-template")
    def template_button(self) -> None:
        self.app.push_screen(TemplateDeploymentScreen())

    @on(Button.Pressed, "#btn-back")
    def back_button(self) -> None:
        self.app.pop_screen()
            
