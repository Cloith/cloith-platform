import asyncio
import json
import os
from services.base_vault import VaultStatus
from screens.password_modal_screen import PasswordModal

class BitwardenClient:
    def __init__(self, app):
        self.app = app
        self.base_command = "bw"

    async def call(self, *args: str) -> dict | str | VaultStatus | None:
        """Centralized CLI handler similar to Hostinger 'request' method."""
        cmd = [self.base_command] + list(args)

        if hasattr(self.app, "bw_session") and self.app.bw_session:
            cmd.extend(["--session", self.app.bw_session])
        else:
            # TODO: make a password prompt for unlocking the vault and getting the token
            self.app.notify("no session token")
            return VaultStatus.MASTER_PASSWORD_PROMPT
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE
            )
            try:
                line = await asyncio.wait_for(process.stderr.read(100), timeout=1.0)
                if b"Master password" in line:
                    process.kill() 
                    return VaultStatus.MASTER_PASSWORD_PROMPT
            except asyncio.TimeoutError:
                pass

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5.0)

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                if "vault is locked" in error_msg.lower():
                    raise PermissionError("Bitwarden vault is locked.")
                elif "not found" in error_msg.lower():
                    return VaultStatus.ITEM_MISSING
            try:
                return json.loads(stdout.decode())
            except json.JSONDecodeError:
                return stdout.decode().strip()
                
        except Exception as e:
            return VaultStatus.UNKNOWN_ERROR
        # return VaultStatus.TIMEOUT
    
    