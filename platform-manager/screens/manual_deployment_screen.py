from textual import on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Static, Footer
from textual.containers import Container
from screens.hostinger.hostinger_vps_picker_screen import HostingerVPSPickerScreen

class ProviderSelectionScreen(Screen):
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
        self.app.push_screen(HostingerVPSPickerScreen())
        