from rich.spinner import Spinner
from textual.widgets import Static

class LoadingSpinner(Static):
    def __init__(self, style: str = "dots", text: str = ""):
        super().__init__("")
        self.spinner = Spinner(style, text=text)

    def on_mount(self) -> None:
        self.set_interval(1 / 10, lambda: self.update(self.spinner))