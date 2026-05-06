from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, ListView, ListItem, Label, Button

class PostInstallScriptForm(Static):
    DEFAULT_CSS = """
        PostInstallScriptForm {
            height: 1fr;
            width: 1fr;
            align: center middle;
        }
        #script-container {
            width: 95%;
            height: 100%;
            keyline: thin;
        }
        #selection-text {
            content-align: center middle;
            color: auto;
            background: $accent;
            dock: top;
        }
        .script-row {
            height: 1;
        }
        .script-name {
            width: 85%; 
            content-align: left middle;
        }
        .icon-btn {
            width: 4;
            height: 1;
            margin: 0 1;
            background: $surface;
            content-align: center middle;
        }
        .icon-btn:hover {
            background: $accent;
            color: $primary;
        }
        .btn-group {
            width: 1fr;
        }
        .edit-btn:hover {
            color: $accent;
            background: $accent;
        }
        .delete-btn:hover {
            color: $error;
            background: $error;
        }
    """
    

    def compose(self) -> ComposeResult:
        with Container(id="script-container"):
            yield Static("Current Selection:", id="selection-text")
            yield ListView()
            
    def on_mount(self):
        self.list = self.query_one(ListView)
        self.run_worker(self.fetch_scripts())
        
    
    async def fetch_scripts(self):
        result = await self.app.vault_service.get_folder("scripts")
        self.populate_list(result)
        
    def populate_list(self, result):
        new_items = []
        
        for script in result:
            name = script.get("name", "Unknown Script")
            row = Horizontal(
                Static(name, classes="script-name"),
                Horizontal(
                    Static("✎", id=f"edit-{name}", classes="icon-btn edit-btn"),
                    Static("🗑", id=f"delete-{name}", classes="icon-btn delete-btn"),
                    classes="btn-group"
                ),
                id=f"row-{name}",
                classes=f"script-row"
            )
            new_items.append(ListItem(row))
        
        if new_items:
            self.list.mount(*new_items)
            