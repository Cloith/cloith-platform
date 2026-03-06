import hashlib
import httpx
import string
from services.password_policy import PasswordPolicy

class PasswordService:
    def __init__(self, policy: PasswordPolicy):
        self.policy = policy

    def validate_rules(self, password: str) -> dict[str, bool]:
        checks = {}
        
        if self.policy.min_length:
            checks["min_length"] = len(password) >= self.policy.min_length

        if self.policy.max_length:
            checks["max_length"] = len(password) <= self.policy.max_length

        if self.policy.require_upper:
            checks["upper"] = any(c.isupper() for c in password)

        if self.policy.require_lower:
            checks["lower"] = any(c.islower() for c in password)

        if self.policy.require_number:
            checks["number"] = any(c.isdigit() for c in password)

        if self.policy.allowed_symbols:
            checks["symbols"] = any(c in self.policy.allowed_symbols for c in password)

        if self.policy.only_latin:
            allowed_chars = string.ascii_letters + string.digits
            if self.policy.allowed_symbols:
                allowed_chars += "".join(self.policy.allowed_symbols)
            
            checks["latin_only"] = all(c in allowed_chars for c in password)

        return checks

    async def is_password_leaked(self, password: str) -> bool:
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=5.0)

                if response.status_code != 200:
                    return False

                hashes = (line.split(':') for line in response.text.splitlines())
                return any(h[0] == suffix for h in hashes)
            except Exception:
                return False
             

    
    # @on(Input.Changed, "#panel-password-input")
    # async def validate_password(self, event: Input.Changed) -> None:
    #     pw = event.value
        
    #     checks = {
    #         "req-length": len(pw) >= 12,
    #         "req-upper": any(c.isupper() for c in pw),
    #         "req-lower": any(c.islower() for c in pw),
    #         "req-number": any(c.isdigit() for c in pw),
    #     }

    #     for req_id, is_valid in checks.items():
    #         widget = self.query_one(f"#{req_id}", Static)
    #         label = self.REQS[req_id]
    #         if is_valid:
    #             widget.update(f"[b green]✔[/] {label}")
    #             widget.add_class("req-valid")
    #         else:
    #             widget.update(f"[b red]✖[/] {label}")
    #             widget.remove_class("req-valid")

    #     leak_widget = self.query_one("#req-leak", Static)
    #     leak_label = self.REQS["req-leak"]
    #     if all(checks.values()):
    #         leak_widget.update(Spinner("dots", text=f" {leak_label}"))
    #         self.run_leak_check(pw)
    #     else:
    #         leak_widget.update(f"[b red]✖[/] {leak_label}")
    #         leak_widget.set_class(False, "req-valid")

    # @work(exclusive=True)
    # async def run_leak_check(self, password: str) -> None:
    #     """Background worker to check for leaks without freezing the UI."""
    #     leak_widget = self.query_one("#req-leak", Static)
        
    #     # Perform the async API call
    #     is_leaked = await self.is_password_leaked(password)
        
    #     # Update the UI based on the result
    #     if is_leaked:
    #         leak_widget.update(f"[red]✖[/] {self.REQS['req-leak']} (Leaked!)")
    #         leak_widget.set_class(False, "req-valid")
    #     else:
    #         leak_widget.update(f"[green]✔[/] {self.REQS['req-leak']}")
    #         leak_widget.set_class(True, "req-valid")
    
