import asyncio
from textual import on, work
from textual.widgets import Static, ProgressBar, Label, LoadingIndicator, Button
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from screens.base_screen import AppScreen
from providers.bitwarden.bitwarden_vault_service import BaseVaultService
from services.base_vault import VaultStatus
from screens.password_modal_screen import PasswordModal

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
                    yield LoadingIndicator(id="loading-animation")
                    yield Static("Fetching Data, Please wait...", id="loading-text")
                    with Container(id="button-container"):
                        yield Button("Try Again", variant="primary", id="try-again-button")
                        yield Button("Authorize", variant="primary", id="authorize-button")
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
        self.main_container = self.query_one("#main-container")
        self.loading_text = self.query_one("#loading-text")
        self.run_worker(self.template_data_fetcher())
        
    async def template_data_fetcher(self):
        self.main_container.add_class("loading-state")
        self.main_container.remove_class("item-not-found", "unknown-error", "password-prompt")
        result = await self.vault_service.get_secrets("template_data")
        self.main_container.remove_class("loading-state")

        if result == VaultStatus.ITEM_MISSING:
            self.main_container.add_class("item-not-found")
            self.loading_text.update( 
                "[orange]No active infrastructure detected[/].\n"
                "Use the [yellow bold]Provisioning Manager[/] to get started."
            )
            sidebar = self.query_one("#sidebar")
            if "expand" not in sidebar.classes:
                sidebar.add_class("expand")
                self.run_worker(self.flash_provisioning_button())
        elif result == VaultStatus.UNKNOWN_ERROR:
            self.main_container.add_class("unknown-error")
            self.loading_text.update(
                "[red]Unkown Error[/].\n"
                "Something went wrong. Please check your connection and [blue]try again.[/]"
            )
        elif result == VaultStatus.MASTER_PASSWORD_PROMPT:
            self.main_container.add_class("password-prompt")
            self.loading_text.update(
                "[red]Authentication Required[/].\n"
                "Something went wrong while accessing your vault. Please [blue]authorize[/] to continue."
            )
    
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

    @on(Button.Pressed, "#try-again-button")
    async def try_again(self) -> None:
        self.main_container.add_class("loading-state")
        self.loading_text.update("Retrying connection...")
        await asyncio.sleep(0.5)
        self.run_worker(self.template_data_fetcher())
    
    @on(Button.Pressed, "#authorize-button")
    @work
    async def password_modal(self) -> None:
        password = await self.app.push_screen_wait(PasswordModal())
        if password:
            self.main_container.add_class("loading-state")
            self.loading_text.update("Refreshing token, please wait...")
            self.main_container.remove_class("password-prompt")
        elif not password:
            return

    # @on(Button.Pressed, "#deployment-manager-button")
    # def deploy_button(self) -> None:
    #     self.app.push_screen(DeploymentScreen())


        

