import asyncio
import json

class BitwardenClient:
    def __init__(self, app):
        self.app = app
        self.base_command = "bw"

    async def call(self, *args: str) -> dict | str:
        """Centralized CLI handler similar to Hostinger 'request' method."""
        cmd = [self.base_command] + list(args)

        if hasattr(self.app, "bw_session") and self.app.bw_session:
            cmd.extend(["--session", self.app.bw_session])
        else:
            # TODO: make a password prompt for unlocking the vault and getting the token
            self.app.notify("no session token")
        
        try:
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
                elif "not found" in error_msg.lower():
                    return None
                raise Exception(f"Bitwarden CLI Error: {error_msg}")

            try:
                self.app.notify("cli request success")
                return json.loads(stdout.decode())
            except json.JSONDecodeError:
                return stdout.decode().strip()
            
        except Exception as e:
            self.app.notify(f"{e}", severity="error")
            return None

       