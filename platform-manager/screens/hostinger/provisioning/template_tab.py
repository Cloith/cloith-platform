from textual import on, work
from textual.widgets import (
    Static, RadioButton, Input, RadioSet
)
from textual.app import ComposeResult
from providers.hostinger.client import HostingerClient
from textual.worker import Worker
from services.textual_message_bus import DescriptionUpdate, ButtonDescriptionUpdate
from providers.hostinger.template_service import HostingerTemplateService

class TemplateTab(Static):
 
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search bar", id="search-bar")
        with RadioSet():
            None
    
    def on_mount(self) -> None:
        self.post_message(DescriptionUpdate("Select a template from the list to view its description"))
        self.new_buttons = []
        client = HostingerClient(self.app.hostinger_token)
        self.template_service = HostingerTemplateService(client)
        self.fetch_templates()
    
    @work(exclusive=True, name="template_fetcher")
    async def fetch_templates(self) -> None:
        try:
            vps_list = await self.template_service.get_all_templates()
            
            return vps_list
        except Exception as e:
            self.notify(f"Failed to fetch templates: {e}", severity="error")

    @on(Worker.StateChanged)
    def handle_template_result(self, event: Worker.StateChanged) -> None:
        if event.worker.name == "template_fetcher" and event.worker.is_finished:
            result = event.worker.result
            if isinstance(result, list):
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
                self.populate_list(self.new_buttons)
            else:
                self.notify(f"Error fetching templates: {result}", severity="error")

    def populate_list(self, buttons_to_show: list[RadioButton]) -> None:
        radio_set = self.query_one(RadioSet)
        radio_set.query("RadioButton").remove()
        if buttons_to_show:
            radio_set.mount(*buttons_to_show)

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
            self.new_desc = self.template_descriptions.get(selected_button.id, "No description found.")
            self.post_message(ButtonDescriptionUpdate(self.new_desc))


        


           
   