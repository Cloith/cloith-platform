from textual.message import Message

class DescriptionUpdate(Message):
    """Sent when the tab description needs to change."""
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()

class GlobalRetryRequested(Message):
    """Sent when a session token (Vault/Provider) is successfully updated."""


