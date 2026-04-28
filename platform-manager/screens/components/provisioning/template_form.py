from textual import on, work
from textual.widgets import (
    Static, RadioButton, Input, RadioSet
)
from textual.app import ComposeResult
from textual.worker import Worker
from textual.containers import Container
from custom_widgets.state_overlay import StateOverlay
from core.handlers import ServiceResponseHandler
from models.status import ResponseStatus
from services.textual_message_bus import DescriptionUpdate, GlobalRetryRequested

class TemplateForm(Static):
 
    def compose(self) -> ComposeResult:
        yield StateOverlay(id="overlay")
        yield Input(placeholder="Search bar", id="search-bar")    
        with RadioSet():
            None
    
    def on_mount(self) -> None:
        self.post_message(DescriptionUpdate("Select a template from the list to view its description"))
        self.new_buttons = []
        self.template_descriptions = {}
        self.overlay = self.query_one("#overlay")
        self.run_worker(self.fetch_templates())
    
    def restart_request(self) -> None:
        self.run_worker(self.fetch_templates())
    
   
    async def fetch_templates(self) -> None:
        self.overlay.enter_loading("fetching os template list, pleas wait...")
        result = await self.app.provider_service.get_all_templates()

        self.app.refresh()

        if isinstance(result, ResponseStatus):
            self.overlay.enter_error(ServiceResponseHandler(self.app).get_config(response=result, type="overlay"))
        else:
            self.overlay.hide_loading()
            self.template_descriptions = {
                f"os-{tpl.get('id')}": tpl.get("description", "No description available.")
                for tpl in result
            }
            self.new_buttons = [
                RadioButton(
                    tpl.get("name", "Unknown OS"),
                    id=f"os-{tpl.get('id')}",
                    classes="os-buttons"
                )
                for tpl in result
            ]
            await self.populate_list(self.new_buttons)

    async def populate_list(self, buttons_to_show: list[RadioButton]) -> None:
        radio_set = self.query_one(RadioSet)
        await radio_set.query("RadioButton").remove()
        if buttons_to_show:
            await radio_set.mount(*buttons_to_show)

    @on(Input.Changed, "#search-bar")
    def handle_search(self, event: Input.Changed) -> None:
        """Refresh the list whenever the user types in the search box."""
        search_value = event.value.strip().lower()
        
        if not search_value:
            self.populate_list(self.new_buttons)
        else:
            filtered_templates = [
                btn for btn in self.new_buttons
                if search_value in str(btn.label).lower()
            ]
            self.populate_list(filtered_templates)

    @on(RadioSet.Changed)
    def update_description_text(self, event: RadioSet.Changed) -> None:
        """Updates the static text whenever an OS RadioButton is toggled."""
        selected_button = event.pressed
        if selected_button:
            new_desc = self.template_descriptions.get(selected_button.id, "No description found.")
            self.post_message(DescriptionUpdate(new_desc))