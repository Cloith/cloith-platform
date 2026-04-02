import asyncio
from textual import on
from textual.widgets import Static, ProgressBar, Label, Button
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from screens import BaseScreen
from services.base_vault import VaultStatus
from screens.provisioning_manager import ProvisioningManagerScreen
from custom_widgets.state_overlay import StateOverlay

class DashboardScreen(BaseScreen):
    CSS_PATH = "tcss/dashboard_screen.tcss"

    def setup_content(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            with Container(id="sidebar"):
                yield Button("[bold]¤[/bold]", variant="primary", id="menu-toggle")
                with Container(id="sidebar-buttons-container"):
                    yield Button("Provisioning Manager", variant="primary", id="provisioning-manager-button")
            with Container(id="dashboard-info-container"):
                with Vertical(id="overlay-container"):
                    yield StateOverlay(id="status-overlay")
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
        self.overlay = self.query_one("#status-overlay")
        self.main_container = self.query_one("#main-container")
        self.sidebar = self.query_one("#sidebar")
        self.run_worker(self.template_data_fetcher())
        
    async def template_data_fetcher(self):
        self.overlay.enter_loading("Fetching Data, Please wait...")
        result = await self.app.vault_service.get_item("template_data")

        if result == VaultStatus.ITEM_MISSING:

            message = """[orange]No active infrastructure detected[/] \n\n Use the [yellow bold]Provisioning Manager[/] to get started."""
            self.overlay.enter_error(message, show_retry = False, show_auth = False)
            
            if "expand" not in self.sidebar.classes:
                self.sidebar.add_class("expand")
                self.run_worker(self.flash_provisioning_button())

        elif result == VaultStatus.UNKNOWN_ERROR:
            message = """[red]Unkown Error[/] \n\n Something went wrong.\n Please check your connection and [blue]try again.[/]"""
            self.overlay.enter_error(message, show_retry = True, show_auth = False)
            
        elif result == VaultStatus.MASTER_PASSWORD_PROMPT:
            message = """[red]Authentication Required[/] \n\n Something went wrong while accessing your vault.\n Please [blue]authorize[/] to continue."""
            self.overlay.enter_error(message, show_retry = False, show_auth = True)
    
    async def flash_provisioning_button(self) -> None:
        button = self.query_one("#provisioning-manager-button")
        for _ in range(4): 
            button.add_class("highlight-flash")
            await asyncio.sleep(0.4)
            button.remove_class("highlight-flash")
            await asyncio.sleep(0.2)

    @on(Button.Pressed, "#menu-toggle")
    def menu_button(self) -> None:
        self.query_one("#sidebar").toggle_class("expand")

    @on(Button.Pressed, "#provisioning-manager-button")
    def deploy_button(self) -> None:
        self.app.push_screen(ProvisioningManagerScreen())

    @on(StateOverlay.RetryRequested)
    def restart_request(self) -> None:
        self.run_worker(self.template_data_fetcher())