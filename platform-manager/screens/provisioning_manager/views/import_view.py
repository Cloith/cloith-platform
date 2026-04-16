from textual.widgets import OptionList, Markdown, Label, Button, Static
from textual.containers import Horizontal, VerticalScroll, Vertical, Container
from textual.app import ComposeResult
from pathlib import Path

class ImportView(Static):
    DEFAULT_CSS = """
    ImportView {
        height: 100%;
    }

    #btn-container {
        height: 5;
        position: relative;
        align: center bottom;
    }

    #template-options {
        height: 1fr;
    }

    #template-list {
        height: 100%;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="template-list"):
            yield Label("Available Templates:")
            yield OptionList(id="template-options")
            with Container(id="btn-container"):
                yield Button("Import", variant="success", id="import-btn")

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