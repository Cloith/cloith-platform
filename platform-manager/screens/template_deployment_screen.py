from textual import work, on
from textual.widgets import OptionList, Markdown, Label, Footer, Header, Button
from textual.containers import Horizontal, VerticalScroll, Vertical
from textual.screen import Screen
from textual.app import ComposeResult
from pathlib import Path

class TemplateDeploymentScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="sidebar-list"):
                yield Label("Available Templates")
                yield OptionList(id="template-options")
            
            with VerticalScroll(id="details-pane"):
                yield Markdown(id="template-readme")
        
        with Horizontal(id="action-bar"):
            yield Button("Deploy Selected", variant="success", id="start-deploy")
            yield Button("Back", id="back-btn")
        yield Footer()

    def on_mount(self) -> None:
        self.scan_templates()

    def scan_templates(self):
        p = Path("./templates")
        if p.exists():
            templates = [d.name for d in p.iterdir() if d.is_dir()]
            self.query_one("#template-options").add_options(templates)
            
    @on(Button.Pressed, "#back-btn")
    def go_back(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # self.deploy_template()
        None

    # @work(thread=True)
    # def deploy_template(self):
    #     None

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Update the README view when the user moves the selection highlight."""
        template_name = str(event.option.prompt)
        readme_path = Path(f"./templates/{template_name}/README.md")
        
        if readme_path.exists():
            content = readme_path.read_text()
            self.query_one("#template-readme").update(content)
        else:
            self.query_one("#template-readme").update("# No Description Found\nAdd a README.md to this template folder.")