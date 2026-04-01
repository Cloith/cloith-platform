from textual import work, on
from textual.worker import Worker
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import Static, OptionList, Button, LoadingIndicator
from core.exceptions import ItemNotFoundError, InvalidItemError
from services.base_vps import VPSStatus
from services.base_vault import VaultStatus
from screens.base_screen import AppScreen
from screens.modal_screen import PasswordModal

class VPSPickerScreen(AppScreen):
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

    #main-content {
        align: center middle;
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

    #vps-list {
        height: 1fr;
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
        self.run_worker(self.fetch_vps_list())
        
    async def fetch_vps_list(self):
        result = await self.app.vps_service.get_all_vps()

        if result == VPSStatus.TOKEN_MISSING:
            token_name = f"{self.app.vps_service.provider_name}_token"
            auth_result = await self.app.vault_service.get_item(token_name)
            
            if auth_result == VPSStatus.SUCCESS:
                return await self.fetch_vps_list()
            elif auth_result == VPSStatus.TOKEN_MISSING:
                self.app.notify("still missing")
            elif auth_result == VaultStatus.MASTER_PASSWORD_PROMPT:
                result = await self.app.push_screen_wait(PasswordModal())
            
        elif result == VPSStatus.TOKEN_INVALID:
            self.app.notify("token invalid")
        
        
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
            
           

            

        
