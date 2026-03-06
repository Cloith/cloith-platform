from textual import work, on
from textual.worker import Worker
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import Static, OptionList, Button, LoadingIndicator
from providers.bitwarden.vault import get_item
from core.exceptions import ItemNotFoundError, InvalidItemError
from providers.hostinger.api import HostingerClient
from screens.base_screen import AppScreen
from screens.hostinger.setup_wizard_screen import SetupWizardScreen
from services.vps_service import HostingerVPSService

class HostingerVPSPickerScreen(AppScreen):
    
    
    CSS = """
    #loading-container {
        display: none;
    }

    .loading #loading-container {
        display: block;
    }

    .loading #main-content {
        display: none;
    }

    #main-container {
        layout: grid;
        grid-size: 2; /* Two columns */
        grid-columns: 1fr 1fr; /* Equal width, or 1fr 2fr if you want more description space */
    }

    #description-container {
        height: 1fr;           /* Take up remaining vertical space */
        overflow-y: auto;    /* Force a scrollbar or use 'auto' */
        padding: 1;
        border: vkey $accent;
        background: $surface;
    }

    #description-container > Static {
        width: 100%;
        height: auto;          /* Allow the static text to be as tall as the text itself */
    }
    """

    def setup_content(self) -> ComposeResult:
        with Vertical(id="loading-container"):
                yield LoadingIndicator()
                yield Static("Fetching Hostinger API key...", id="loading-text")
        with Container(id="main-container"):
            with Vertical(id="main-content"):
                yield Static("Fetching your Hostinger VPS list...", id="status")
                yield OptionList(id="vps-list")
                yield Button("Confirm Selection", variant="success", id="confirm-vps")
            with Vertical(id="description-container"):
                yield Static("")

    def on_mount(self) -> None:
        self.app.hostinger_token = "sMHeus9AiOMhlsFgPkxeoSVBMlVqArF39sroGMBe36b79ebe"
        if hasattr(self.app, "hostinger_token") and self.app.hostinger_token:
            client = HostingerClient(self.app.hostinger_token)
            self.vps_service = HostingerVPSService(client)
            self.remove_class("loading")
            self.fetch_vps_list() 
        else:
            self.add_class("loading")
            self.fetch_hostinger_token()

    @work(thread=True, name="token_fetcher")
    def fetch_hostinger_token(self):
        try:
            return get_item("hostinger_token", self.app.bw_session)
        except Exception as e:
            return e
        
    @work(thread=True, name="vps_fetcher")
    async def fetch_vps_list(self):
        try:
            vps_list = await self.vps_service.get_all_vps()
            return vps_list
        except Exception as e:
            return e
    
    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.worker.is_finished:
            result = event.worker.result
            
            if event.worker.name == "token_fetcher":
                if isinstance(result, (InvalidItemError, ItemNotFoundError)):
                    self.notify(str(result), severity="error")
                    self.remove_class("loading")
                elif isinstance(result, Exception):
                    self.notify("An unexpected error occurred", severity="error")
                else:
                    self.app.hostinger_token = result
                    self.fetch_vps_list() 

            elif event.worker.name == "vps_fetcher":
                self.remove_class("loading") 
                if isinstance(result, list):
                    self.app.vps_inventory = result 
                    self.populate_list(result) 
                else:
                    self.notify(f"VPS Fetch Failed: {result}", severity="error")

    def populate_list(self, vps_data: list) -> None:
        option_list = self.query_one("#vps-list", OptionList)
        option_list.clear_options()
        
        for vps in vps_data:
            hostname = vps.name
            status = vps.status
            option_list.add_option(f"{hostname} [{status}]")

    @on(OptionList.OptionHighlighted)
    def update_description(self, event: OptionList.OptionHighlighted) -> None:
        vps = self.app.vps_inventory[event.option_index]
        
        details = (
            f"[bold cyan]Name:[/bold cyan] {vps.name}\n"
            f"[bold cyan]Status:[/bold cyan] {vps.status}\n"
            f"[bold cyan]IP Address:[/bold cyan] {vps.ip}\n"
            "-----------------------------------\n"
            f"[bold]CPU:[/bold] {vps.cpu_cores} Cores\n"
            f"[bold]RAM:[/bold] {vps.ram_gb:.0f} GB\n"
            f"[bold]Disk:[/bold] {vps.disk_gb:.0f} GB\n"
            f"[bold]Disk:[/bold] {vps.os_name} GB\n"
        )
        self.query_one("#description-container Static", Static).update(details)

    @on(Button.Pressed, "#confirm-vps")
    def confirm_button(self) -> None:
        option_list = self.query_one("#vps-list", OptionList)
        
        if option_list.highlighted is not None:
            selected_vps = self.app.vps_inventory[option_list.highlighted]
            
            self.app.push_screen(SetupWizardScreen(selected_vps))
        else:
            self.notify("Please select a VPS from the list first.", severity="warning")
            
           

            

        
