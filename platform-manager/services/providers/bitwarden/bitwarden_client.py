import asyncio
import json
from models.status import ResponseStatus
from core.handlers import ClientRequestHandler

class BitwardenClient:
    def __init__(self, app):
        self.app = app
        self.base_command = "bw"
        self.session_exempt_commands = ["unlock", "login"]

    async def call(self, *args: str) -> dict | str | ResponseStatus | None:
        """Centralized CLI handler similar to Hostinger 'request' method."""

        cmd = [self.base_command] + list(args)

        is_exempt = any(cmd_type in args for cmd_type in self.session_exempt_commands)

        if not is_exempt:
            if not self.app.vault_session or self.app.vault_session == "":
                return ResponseStatus.MASTER_PASSWORD_PROMPT
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
                    return ResponseStatus.MASTER_PASSWORD_PROMPT
                elif b"You are not logged in." in chunk:
                    return ResponseStatus.UNKNOWN_ERROR
                
                stored_stderr = chunk
            except asyncio.TimeoutError:
                stored_stderr = b""

            stdout, stderr_remaining = await asyncio.wait_for(process.communicate(), timeout=5.0)
            full_stderr = stored_stderr + stderr_remaining
            
            if process.returncode != 0:
                error_msg = full_stderr.decode().strip()
                response = ResponseStatus.UNKNOWN_ERROR # Default

                if "decryption operation failed" in error_msg or "provided key is not the expected type" in error_msg:
                    response = ResponseStatus.WRONG_PASSWORD
                elif "vault is locked" in error_msg.lower():
                    response = ResponseStatus.MASTER_PASSWORD_PROMPT
                elif "not found" in error_msg.lower():
                    response = ResponseStatus.TOKEN_MISSING
                
                return ClientRequestHandler.get_config(self, response=response)
            try:
                result = json.loads(stdout.decode())
                return result
            except json.JSONDecodeError:
                return stdout.decode().strip()
                
        except Exception as e:
            ClientRequestHandler.get_config(self, response=ResponseStatus.UNKNOWN_ERROR)
    