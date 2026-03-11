import hashlib
import httpx
import string
from models.password import PasswordPolicy

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
            
    