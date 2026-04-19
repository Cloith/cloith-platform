from dataclasses import dataclass

@dataclass
class OverlayConfig:
    message: str
    mode: str = "vault"
    show_retry: bool = False
    show_auth: bool = False
    show_unlock: bool = False
    show_update: bool = False
    show_buy: bool = False
    button_label: str = "Authorize"