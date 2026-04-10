import asyncio
from textual import on
from textual.widgets import Static, Button
from textual.containers import VerticalScroll
from textual.app import ComposeResult

class NavigationSidebar(Static):
    DEFAULT_CSS = """
    NavigationSidebar {
        width: 5;
        height: 100%;
        background: $boost;
        transition: width 300ms in_out_cubic;
    }

    NavigationSidebar.expand {
        width: 25;
    }

    #menu-toggle  {
        height: 1;
        margin: 1;
        border: none;
        min-width: 0;
        background: $accent;
    }

    #nav-container {
        opacity: 0%;
        visibility: hidden; 
        transition: opacity 500ms in_out_cubic;
        width: 100%;
    }

    NavigationSidebar.expand #nav-container {
        opacity: 100%;
        visibility: visible;
        transition: width 300ms in_out_cubic;
    }

    #sidebar-header {
        content-align: center middle;
        margin-bottom: 1;
    }

    .nav-btn {
        width: 100%;
        align: center middle;
    }

    #nav-dashboard {
        display: block;
    }

    .nav-btn.highlight-flash {
        background: $warning;     
        color: $text;
        text-style: bold italic;
        border: tall $error;     
    }
    """

    def on_mount(self) -> None:
        self.update_sidebar()

    def on_screen_resume(self) -> None:
        self.update_sidebar()

    def update_sidebar(self) -> None:
            class_name = self.app.screen.__class__.__name__
            self.query_one("#nav-dashboard").display = (class_name != "DashboardScreen")
            self.query_one("#nav-provisioning").display = (class_name != "ProvisioningManagerScreen")


    def compose(self) -> ComposeResult:
            yield Button("[bold]¤[/bold]", variant="primary", id="menu-toggle")
            with VerticalScroll(id="nav-container"):
                yield Static("[b]NAVIGATION[/b]", id="sidebar-header")
                yield Button("Dashboard", id="nav-dashboard", classes="nav-btn")
                yield Button("Provisioning Manager", id="nav-provisioning", classes="nav-btn")

    @on(Button.Pressed)
    def handle_navigation(self, event: Button.Pressed) -> None:
        """Centralized routing for the whole app."""
        from screens.core.dashboard_screen import DashboardScreen
        from screens.provisioning_manager import ProvisioningManagerScreen
        nav_id = event.button.id
        
        if nav_id == "menu-toggle":
            self.toggle_class("expand")
        elif nav_id == "nav-dashboard":
            self.app.switch_screen(DashboardScreen())
        elif nav_id == "nav-provisioning":
            self.app.switch_screen(ProvisioningManagerScreen())

    async def flash_provisioning_button(self, button_name: str) -> None:
        button = self.query_one(f"#{button_name}")
        if "expand" not in self.classes:
            self.add_class("expand")
        for _ in range(4): 
            button.add_class("highlight-flash")
            await asyncio.sleep(0.4)
            button.remove_class("highlight-flash")
            await asyncio.sleep(0.2)
