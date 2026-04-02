import asyncio
import json
from services.base_vault import VaultStatus

class BitwardenClient:
    def __init__(self, app):
        self.app = app
        self.base_command = "bw"
        self.session_exempt_commands = ["unlock", "login"]

    async def call(self, *args: str) -> dict | str | VaultStatus | None:
        """Centralized CLI handler similar to Hostinger 'request' method."""

        cmd = [self.base_command] + list(args)

        is_exempt = any(cmd_type in args for cmd_type in self.session_exempt_commands)

        if not is_exempt:
            if not self.app.vault_session or self.app.vault_session == "":
                return VaultStatus.MASTER_PASSWORD_PROMPT
            else:
                cmd.extend(["--session", self.app.vault_session])

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            try:
                chunk = await asyncio.wait_for(process.stderr.read(1024), timeout=1.0)
                if b"Master password" in chunk:
                    process.kill()
                    return VaultStatus.MASTER_PASSWORD_PROMPT
                elif b"You are not logged in." in chunk:
                    return VaultStatus.UNKNOWN_ERROR
                
                stored_stderr = chunk
            except asyncio.TimeoutError:
                stored_stderr = b""

            stdout, stderr_remaining = await asyncio.wait_for(process.communicate(), timeout=5.0)
            full_stderr = stored_stderr + stderr_remaining
            
            if process.returncode != 0:
                error_msg = full_stderr.decode().strip()
                if "decryption operation failed" in error_msg or "provided key is not the expected type" in error_msg:
                    return VaultStatus.WRONG_PASSWORD
                elif "vault is locked" in error_msg.lower():
                    raise VaultStatus.MASTER_PASSWORD_PROMPT
                elif "not found" in error_msg.lower():
                    return VaultStatus.ITEM_MISSING
            try:
                result = json.loads(stdout.decode())
                return result
            except json.JSONDecodeError:
                return stdout.decode().strip()
                
        except Exception as e:
            return VaultStatus.UNKNOWN_ERROR
    
    