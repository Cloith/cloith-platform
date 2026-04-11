from textual.widgets import OptionList, Markdown, Label, Button, Static
from textual.containers import Horizontal, VerticalScroll, Vertical
from textual.app import ComposeResult
from pathlib import Path

class ImportView(Static):
    DEFAULT_CSS = """
    #action-bar {
        height: 3;
        position: relative;
        align: center middle;
    }

    #template-options {
        height: 10;
    }

    #start-deploy {
        height: 3;
        width: auto;
    }

    #main-container {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-container"):
            with Vertical(id="template-list"):
                yield Label("Available Templates:")
                yield OptionList(id="template-options")

        with Horizontal(id="action-bar"):
            yield Button("Deploy", variant="success", id="start-deploy")

    def on_mount(self) -> None:
        self.scan_templates()

    def scan_templates(self):
        p = Path("./templates")
        if p.exists():
            templates = [d.name for d in p.iterdir() if d.is_dir()]
            self.query_one("#template-options").add_options(templates)

    # def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
    #     """Update the README view when the user moves the selection highlight."""
    #     template_name = str(event.option.prompt)
    #     readme_path = Path(f"./templates/{template_name}/README.md")
        
    #     if readme_path.exists():
    #         content = readme_path.read_text()
    #         self.query_one("#template-readme").update(content)
    #     else:
    #         self.query_one("#template-readme").update("# No Description Found\nAdd a README.md to this template folder.")