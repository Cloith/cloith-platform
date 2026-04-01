from textual import on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Static, Footer
from textual.containers import Container
from screens.vps_picker_screen import VPSPickerScreen
from services.service_factory import get_vps_service

class ProviderSelectionScreen(Screen):
    def __init__(self): 
        super().__init__()
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("SELECT INFRASTRUCTURE PROVIDER", id="title")
        
        with Container(id="provider-grid"):
            yield Button("HOSTINGER", variant="primary", id="hostinger-button")
            yield Button("Back", variant="primary", id="bck-btn")
            yield Button("AWS (Coming Soon)", variant="default", id="provider-aws", disabled=True)
            yield Button("GCP (Coming Soon)", variant="default", id="provider-gcp", disabled=True)
            yield Button("DigitalOcean (Coming Soon)", variant="default", id="provider-do", disabled=True)
        yield Footer()

    @on(Button.Pressed, "#bck-btn")
    def back_button(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#hostinger-button")
    def hostinger_button(self) -> None:
        service = get_vps_service("hostinger", self.app)
        self.app.vps_service = service
        self.app.push_screen(VPSPickerScreen())
        