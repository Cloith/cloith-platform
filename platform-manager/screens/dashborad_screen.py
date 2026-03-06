from textual import work, on
from textual.widgets import Static, Header, Footer, ProgressBar, Label, LoadingIndicator, Button
from textual.screen import Screen
from textual.worker import Worker
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from core.exceptions import ItemNotFoundError, InvalidItemError
from providers.bitwarden.vault import get_item
from screens.secrets_screen import SecretsScreen
from screens.deployment_screen import DeploymentScreen

key = "gZgZoXsvC6YThWgzL8pUYj0ev0VFpjEQYNLIvRZl7VBgam4aKnSNoM38R9Pc+fkpgmBnntyXDT8A2vPkIIQm2g=="

class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Button("☰", variant="primary", id="menu-toggle")
        yield Button("Secret Manager", variant="primary", id="secret-manager-button")
        yield Button("Deployment Manager", variant="primary", id="deployment-manager-button")


class DashboardScreen(Screen):
    CSS_PATH = "dashboard_screen.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-body"):
            
            yield Sidebar(id="sidebar")
            with Container(id="dashboard-grid"):
                with Vertical(id="loading-container"):
                    yield LoadingIndicator()
                    yield Static("Loading Metrics...", id="loading-text")
                with Horizontal(id="metrics-row"):
                    with Vertical(classes="metric-card"):
                        yield Label("CPU USAGE")
                        yield ProgressBar(total=180, show_percentage=True, id="cpu-bar")
                    with Vertical(classes="metric-card"):
                        yield Label("MEM USAGE")
                        yield ProgressBar(total=180, show_percentage=True, id="mem-bar")

                with Vertical(id="details-container"):
                    yield Static("VPS INFORMATION", classes="section-title")
                    yield Static("IP Address: 123.456.78.90", classes="data-line")
                    yield Static("Location: Singapore", classes="data-line")
                    yield Static("Status: [green]RUNNING[/green]", classes="data-line")
        yield Footer()

    def on_mount(self) -> None:
        self.app.bw_session = key
        self.template_checker()
        

    @work(thread=True, name="checker")
    def template_checker(self):
        try:
            return get_item("TEMPLATE_DATA", self.app.bw_session)
        except Exception as e:
            return e

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle the outcome of the template check on the Main Thread."""
        if event.worker.name == "checker" and event.worker.is_finished:
            result = event.worker.result

            if isinstance(result, ItemNotFoundError):
                self.query_one("#dashboard-grid").remove_class("loading")
                self.query_one("#loading-text").update("Please deploy your template first")
                self.notify("No active template found, Redirecting to Secret Manager...", severity="warning")
                self.app.push_screen(DeploymentScreen())
                pass
                
            elif isinstance(result, Exception):
                self.notify("Vault data corrupted!", severity="error")
                pass
                    
            else:
                self.query_one("#dashboard-grid").remove_class("loading")
                self.notify("Unexpected error", severity="error")
                pass
    
    @on(Button.Pressed, "#menu-toggle")
    def menu_button(self) -> None:
        self.query_one("#sidebar").toggle_class("collapsed")

    @on(Button.Pressed, "#deployment-manager-button")
    def deploy_button(self) -> None:
        self.app.push_screen(DeploymentScreen())


        

