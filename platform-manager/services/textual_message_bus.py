from textual.message import Message

class DescriptionUpdate(Message):
    """Sent when the tab description needs to change."""
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()

class ButtonDescriptionUpdate(Message):
    """Sent when the OS description needs to change."""
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()
