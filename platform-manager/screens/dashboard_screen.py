import asyncio
from textual import on
from textual.widgets import Static, Header, Footer, ProgressBar, Label, LoadingIndicator, Button
from textual.screen import Screen
from textual.worker import Worker
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from core.exceptions import ItemNotFoundError, InvalidItemError
from screens.secrets_screen import SecretsScreen
from screens.base_screen import AppScreen
from screens.deployment_screen import DeploymentScreen
from providers.bitwarden.bitwarden_vault_service import BaseVaultService

class DashboardScreen(AppScreen):
    CSS_PATH = "dashboard_screen.tcss"

    def __init__(self, vault_service: BaseVaultService):
        super().__init__()
        self.vault_service = vault_service 

    def setup_content(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            with Container(id="sidebar"):
                yield Button("[bold]¤[/bold]", variant="primary", id="menu-toggle")
                with Container(id="sidebar-buttons-container"):
                    yield Button("Provisioning Manager", variant="primary", id="deployment-manager-button")
            with Container(id="dashboard-info-container"):
                with Vertical(id="loading-container"):
                    yield LoadingIndicator()
                    yield Static("Fetching Data, Please wait...", id="loading-text")
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

    def on_mount(self) -> None:
        self.run_worker(self.template_data_fetcher())
        
    async def template_data_fetcher(self):
        item = await self.vault_service.get_secrets("template_data")

        if not item:
            self.query_one("#loading-text").update(
                "[orange]No active infrastructure detected[/].\n"
                "Use the [yellow bold]Provisioning Manager[/] to get started."
            )

            sidebar = self.query_one("#sidebar")
            if "expand" not in sidebar.classes:
                sidebar.add_class("expand")
                self.run_worker(self.flash_provisioning_button())
    
    async def flash_provisioning_button(self):
        button = self.query_one("#deployment-manager-button")
        for _ in range(4): 
            button.add_class("highlight-flash")
            await asyncio.sleep(0.4)
            button.remove_class("highlight-flash")
            await asyncio.sleep(0.2)

    @on(Button.Pressed, "#menu-toggle")
    def menu_button(self) -> None:
        self.query_one("#sidebar").toggle_class("expand")

    # @on(Button.Pressed, "#deployment-manager-button")
    # def deploy_button(self) -> None:
    #     self.app.push_screen(DeploymentScreen())


        

