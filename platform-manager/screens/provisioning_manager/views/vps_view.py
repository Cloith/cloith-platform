from textual import on
from textual.worker import Worker
from textual.app import ComposeResult
from textual.containers import Vertical, Container
from textual.widgets import Static, OptionList, Button, LoadingIndicator
from core.exceptions import ItemNotFoundError, InvalidItemError
from services.base_vps import VPSStatus
from services.base_vault import VaultStatus
from screens import BaseScreen
from screens.common import PasswordModal
from custom_widgets.state_overlay import StateOverlay, OverlayConfig

class VPSView(Static):
    DEFAULT_CSS = """
    VPSView {
        height: 100%;
        width: 100%;
    }

    #main-container {
        height: 100%;
        align: center middle;
        display: block;
    }

    #main-content {
        align: center middle;
    }

    #list-container {
        height: 90%;
    }

    #vps-list {
        height: 1fr;
    }

    #button-container {
        align: center middle;
        height: 5;
    }

    #overlay {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="main-container"):
            yield StateOverlay(id="overlay")
            with Container(id="button-container"): 
                yield Button("Buy VPS", variant="success", id="buy-btn")
        with Container(id = "list-container"):
            yield OptionList(id="vps-list")
        with Container(id="button-container"): 
            yield Button("Confirm VPS", variant="success", id="confirm-vps")

    def on_mount(self) -> None:
        self.run_worker(self.fetch_vps_list())
        self.overlay = self.query_one("#overlay")
        self.query_one("#buy-btn").display = False
        
    
    @on(StateOverlay.RetryRequested)
    def restart_request(self) -> None:
        self.run_worker(self.fetch_vps_list())

    async def fetch_vps_list(self):
        self.overlay.enter_loading("fetching vps list, pleas wait...")
        result = await self.app.vps_service.get_all_vps()

        if result == VPSStatus.TOKEN_MISSING:
            token_name = f"{self.app.vps_service.provider_name}_token"
            auth_result = await self.app.vault_service.get_item(token_name)
            
            if auth_result == VaultStatus.MASTER_PASSWORD_PROMPT:
                config = OverlayConfig(
                    message="""[red]Authentication Required[/] \n\n Something went wrong while accessing your vault.\n Please [blue]authorize[/] to continue.""",
                    show_auth=  True
                    )
                self.overlay.enter_error(config)
                

            elif isinstance(auth_result, dict):
                token = auth_result.get("login", {}).get("password")
                self.app.provider_token = token
                self.run_worker(self.fetch_vps_list())
            
        elif result == VPSStatus.TOKEN_INVALID:
            self.app.notify("token invalid")
        else:
            self.populate_list(result)

    def populate_list(self, vps_data: list) -> None:
        option_list = self.query_one("#vps-list", OptionList)
        option_list.clear_options()

        if not vps_data:
            config = OverlayConfig(
                message = (
                "[bold ornage]No Active Instances Found[/]\n\n"
                "We couldn't find any VPS linked to your account. Please check if:\n"
                " • Your subscription has [yellow]expired[/]\n"
                " • You need to [blue]Buy[/] a new  VPS instance"
                )
            )
            self.overlay.enter_error(config)
            self.query_one("#buy-btn").display = True
        else:
            self.overlay.display = False
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
            
        else:
            self.notify("Please select a VPS from the list first.", severity="warning")

    @on(Button.Pressed, "#buy-btn")
    def confirm_button(self) -> None:
        self.app.notify("Coming Soon!")
            
           

            

        
