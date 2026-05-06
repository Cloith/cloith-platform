from textual import on
from textual.widgets import Static, ProgressBar, Label
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from screens import BaseScreen
from models import ResponseStatus, ConfigClass
from custom_widgets import StateOverlay
from custom_widgets.sidebar import NavigationSidebar
from core.handlers import ServiceResponseHandler

class DashboardScreen(BaseScreen):
    CSS = """
    #main-container {
        width: 100%;
        height: 100%;
        border: none;
    }

    #dashboard-info-container {
        width: 1fr;
        height: 100%;
    }

    #overlay-container {
        width: 100%;
        height: 100%;
        align: center middle;
        content-align: center middle;
    }
    """

    def setup_content(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            yield NavigationSidebar()
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
        self.sidebar = self.query_one(NavigationSidebar)
        self.main_container = self.query_one("#main-container")
        self.run_worker(self.template_data_fetcher())
        
    async def template_data_fetcher(self):
        self.overlay.enter_loading("Fetching Data, Please wait...")
        result = await self.app.vault_service.get_item("template_data")

        if isinstance(result, ResponseStatus):
            self.overlay.enter_error(ServiceResponseHandler(self.app).get_config(response=result, type="overlay"))
            if result == ResponseStatus.ITEM_MISSING:
                 self.run_worker(self.sidebar.flash_provisioning_button("nav-provisioning"))
        else:
            None    

    @on(StateOverlay.RetryRequested)
    def restart_request(self) -> None:
        self.run_worker(self.template_data_fetcher())