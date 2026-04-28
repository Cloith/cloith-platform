from textual import work
from textual.widgets import Static
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from models.password import PasswordPolicy
from services.password_service import PasswordService
from custom_widgets.rich_spinner import LoadingSpinner
from models.status import ResponseStatus

class PasswordRequirementList(Static):
    DEFAULT_CSS = """
        #password-requiremnts {
            height: 15;
        }
        Horizontal {
            height: 1;
        }
        LoadingSpinner {
            width: 3;
            display: none;
        }
        .state-icon {
            width: 2;
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
                if req['id'] == "check_leak":
                    with Horizontal():
                        yield LoadingSpinner(id="check_leak_spinner")
                        yield Static("[b red]✖[/] ",id=f"{req['id']}_icon", classes="state-icon")
                        yield Static(
                            f"{req['text']}", 
                            id=req['id'], 
                            classes="req-invalid"
                        )
                else:
                    with Horizontal():
                        yield Static("[b red]✖[/] ",id=f"{req['id']}_icon", classes="state-icon")
                        yield Static(
                            f"{req['text']}", 
                            id=req['id'], 
                            classes="req-invalid"
                        )

    def update_requirements_widgets(self, pw: str) -> None:
        """Refreshes the UI icons and colors based on validation results."""
        self.checks = self.password_service.validate_rules(pw)

        for req_id, is_valid in self.checks.items():
            
            widget = self.query_one(f"#{req_id}_icon")
            symbol = "[b green]✔[/]" if is_valid else "[b red]✖[/]"
            widget.update(f"{symbol}")
        
        result = self.check_all_valid()

        if result:
            self.check_for_leak(password=pw, skip=False)
        else:
            self.check_for_leak(password=None, skip=True)
        
        
    def check_all_valid(self) -> bool:
        """
        checks if all of the criteria are all valid except for check_leak
        """
        return all(
            is_valid 
            for req_id, is_valid in self.checks.items() 
            if req_id != "check_leak"
        )
    
    @work(exclusive=True, thread=True)
    async def check_for_leak(self, password: str, skip: bool):
        """
        calls the password service for checking if the inputed password is leaked publicly
        also displays a loading clock animation while performing the validation
        """
        self.skip = skip
        
        if not skip:
            self.skip = False
            self.query_one("#check_leak_icon").display = False
            self.query_one("#check_leak_spinner").display = True
            widget = self.query_one("#check_leak")
            original_content = str(widget.content)
            widget.update("Checking public record... please wait")

            leak = await PasswordService.is_password_leaked(password=password)

            self.query_one("#check_leak_icon").display = True
            self.query_one("#check_leak_spinner").display = False

            if self.skip:
                self.query_one("#check_leak_icon").update("[b red]✖[/]")
                return

            if leak == ResponseStatus.UNKNOWN_ERROR:
                self.query_one("#check_leak_icon").update("[b yellow]⚠[/]")
                widget.update("Leak check failed [u b]Retry?[/]") 
            elif leak:
                widget.update("This password is leaked")
                self.query_one("#check_leak_icon").update("[b red]✖[/]")
            else:
                self.query_one("#check_leak_icon").update("[b green]✔ [/]")
                widget.update(f"{original_content}")
