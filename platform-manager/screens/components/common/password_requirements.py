from textual.widgets import Static
from textual.app import ComposeResult
from textual.containers import Container
from models.password import PasswordPolicy
from services.password_service import PasswordService

class PasswordRequirementList(Static):
    DEFAULT_CSS = """
        #password-requiremnts {
            height: 15;
        }
    """
    def __init__(self, policy: PasswordPolicy, **kwargs):
        """
        A reactive UI component for displaying password strength criteria.

        This component dynamically renders a list of requirements derived from a 
        'PasswordPolicy' dataclass. It listens for validation updates and toggles 
        visual states (icons and CSS classes) to provide real-time feedback.

        Attributes:
            policy (PasswordPolicy): The configuration object defining the rules.
        """
        super().__init__(**kwargs)
        self.policy = policy
        self.password_service = PasswordService(policy)
        

    def compose(self) -> ComposeResult:
        with Container(id="password-requiremnts"):
            for req in self.policy.get_requirements_data():
                yield Static(
                    f"[b red]✖[/] {req['text']}", 
                    id=req['id'], 
                    classes="req-invalid"
                )

    def update_requirements_widgets(self, pw: str) -> None:
        """Refreshes the UI icons and colors based on validation results."""
        checks = self.password_service.validate_rules(pw)

        for req_id, is_valid in checks.items():
            try:
                widget = self.query_one(f"#{req_id}", Static)
                
                req_data = next(
                    item for item in self.policy.get_requirements_data() 
                    if item["id"] == req_id
                )
                original_text = req_data["text"]

                symbol = "[b green]✔[/]" if is_valid else "[b red]✖[/]"
                widget.update(f"{symbol} {original_text}")

                widget.set_class(is_valid, "req-valid")
                widget.set_class(not is_valid, "req-invalid")
                
            except Exception:
                continue


