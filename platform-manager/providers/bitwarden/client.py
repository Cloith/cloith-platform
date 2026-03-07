import asyncio
import json

class BitwardenClient:
    def __init__(self, session_token: str | None = None):
        self.session_token = session_token
        self.base_command = "bw"

    async def call(self, *args: str) -> dict | str:
        """Centralized CLI handler similar to Hostinger 'request' method."""
        
        cmd = [self.base_command] + list(args)
        if self.session_token:
            cmd.extend(["--session", self.session_token])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            if "vault is locked" in error_msg.lower():
                raise PermissionError("Bitwarden vault is locked.")
            raise Exception(f"Bitwarden CLI Error: {error_msg}")

        try:
            return json.loads(stdout.decode())
        except json.JSONDecodeError:
            return stdout.decode().strip()