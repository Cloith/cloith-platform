from textual.widgets import (
    Static, Button
)
from textual.containers import VerticalScroll
from textual.app import ComposeResult
from services.providers.hostinger import HostingerProviderService


class ProviderView(Static):
    DEFAULT_CSS = """
    ProviderView {
        align: center middle;
        width: 100%;
        height: 1fr;
    }

    #button-stack {
        width: 1fr;           
        height: 1fr;
        background: $boost;
        align: center middle;
    }

    #button-stack Button {
        width: 100%;   
        padding: 1;     
    }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="button-stack"):
            yield Button("Hostinger", id="hostinger-btn", variant="primary")
            yield Button("AWS", id="aws-btn")
            yield Button("GCP", id="gcp-btn")
            yield Button("Azure", id="azure-btn")

    def on_button_pressed(self, event: Button.Pressed):
        from screens.provisioning_manager import ProvisioningManagerScreen

        if event.button.id == "hostinger-btn":
            self.screen.recipe.provider = "Hostinger"
            self.screen.mutate_reactive(ProvisioningManagerScreen.recipe)
            
            self.app.provider_service = HostingerProviderService(self.app)
        else:
            self.app.notify("Coming Soon!")