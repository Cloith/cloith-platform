from textual import on
from textual.widgets import (
    Static, TabbedContent, TabPane, 
)
from textual.containers import Container, Vertical
from textual.app import ComposeResult
from screens.provisioning_manager.components import TemplateTab
from screens.provisioning_manager.components import PolicyPasswordForm
from services.textual_message_bus import DescriptionUpdate, ButtonDescriptionUpdate
from models.password import PANEL_PASSWORD_POLICY, VPS_PASSWORD_POLICY


class ProvisioningView(Static):
    def compose(self) -> ComposeResult:
        with Vertical(id="provisioning-form"):
            with TabbedContent():
                with TabPane("OS TEMPLATE(REQUIRED)", id="template-tab"):
                    yield Container(TemplateTab(), id="template-container")                                   
                with TabPane("PANEL PASSWORD", id="panel-password-tab"):
                    yield Container(PolicyPasswordForm(policy=PANEL_PASSWORD_POLICY), id="panel-password-container")
                with TabPane("VPS PASSWORD", id="vps-password-tab"):
                    yield Container(PolicyPasswordForm(policy=VPS_PASSWORD_POLICY), id="vps-password-container")
                with TabPane("POST INSTALL SCRIPT", id="script-tab"):
                    yield Static("post install script")

    def on_mount(self) -> None:
        self.last_os_desc = "Select a template from the list to view its description"
    
    @on(TabbedContent.TabActivated)
    def handle_tab_switch(self, event: TabbedContent.TabActivated) -> None:
        active_tab_id = event.pane.id

        if active_tab_id == "template-tab":
            current_desc = getattr(
                self, "last_os_desc", "Select a template from the list to view its description"
            )
            self.post_message(DescriptionUpdate(current_desc))
        elif active_tab_id == "panel-password-tab":
            password_help = (
                "Panel password for the panel-based OS template.\n"
                "If not provided, a random password will be generated.\n\n"
                "[b orange]Password Requirements[/b orange]\n"
                "Password will be checked against leaked databases.\n"
                "Requirements:\n\n"
                " • [b yellow]At least 12 characters long[/b yellow]\n"
                " • [b yellow]At least one uppercase letter[/b yellow]\n"
                " • [b yellow]At least one lowercase letter[/b yellow]\n"
                " • [b yellow]At least one number[/b yellow]\n"
                " • [b yellow]Is not leaked publicly[/b yellow]"
            )
            self.post_message(DescriptionUpdate(password_help))
        elif active_tab_id == "vps-password-tab":
            vps_pass_desc =(
                "Root password for the virtual machine. If not provided, random" \
                "password will be generated. Password will not be shown in the response. \n\n"
                "[b orange]Password Requirements[/b orange]\n\n"
                " • [b yellow]Must have one number[/b yellow]\n"
                " • [b yellow]Must contain one lowercase letter[/b yellow]\n"
                " • [b yellow]Must contain one uppercase letter[/b yellow]\n"
                " • [b yellow]At least 12 characters long[/b yellow]\n"
                " • [b yellow]Maximum 50 characters long[/b yellow]\n"
                " • [b yellow]Only symbols: -().&@?'#,/;+[/b yellow]\n"
                " • [b yellow]Must contain only latin letters[/b yellow]"
                
            )
            self.post_message(DescriptionUpdate(vps_pass_desc))
        elif active_tab_id == "script-tab":
            script_desc = (
                "Post-install script to execute after virtual machine was recreated"
            )
            self.post_message(DescriptionUpdate(script_desc))

    def on_button_description_update(self, message: ButtonDescriptionUpdate) -> None:
        self.last_os_desc = message.text 
        self.post_message(DescriptionUpdate(message.text))