import pexpect
import json
import threading
import re
from models import ResponseStatus
from services import BaseVaultService
from services.providers.bitwarden import BitwardenClient

class BitwardenVaultService(BaseVaultService):
    def __init__(self, app):
        self.app = app
        self._otp_event = threading.Event()
        self.client = BitwardenClient(app)
    
    @property
    def provider_name(self) -> str:
        return "bitwarden"

    def run_login_thread(self, email, password, callback, result_callback):
        """Spawns the worker thread manually."""
        thread = threading.Thread(
            target=self.vault_login, 
            args=(email, password, callback, result_callback),
            daemon=True 
        )
        thread.start()

    def vault_login(self, email, password, otp_callback, result_callback) -> tuple[int, str | None]:
        """
        Runs the pexpect conversation on a separate thread.
        Returns a tuple: (status_code, session_key)
        """

        child= None
        try:
            child = pexpect.spawn(f"bw login {email}", encoding='utf-8', timeout=20)
            child.expect("Master password:")
            child.sendline(password)
            
            next_step = child.expect([
                "Enter OTP sent to login email:",   
                "Two-step login code:",             
                "Invalid master password",         
                "The Email field is not a valid",
                pexpect.TIMEOUT,
                pexpect.EOF
            ])

            if next_step in [0, 1]:
                self.app.call_from_thread(otp_callback)
                self._otp_event.wait()
                self._otp_event.clear()
                
                child.sendline(self.app.otp_code)
                sub_step = child.expect([pexpect.EOF, "invalid new device otp", pexpect.TIMEOUT])
                
                if sub_step == 1: 
                    self.app.call_from_thread(result_callback, (ResponseStatus.INVALID_OTP, None))
                    return
                if sub_step == 2:
                    self.app.call_from_thread(result_callback, (ResponseStatus.TIMEOUT, None))
                    return

            elif next_step == 2:
                self.app.call_from_thread(result_callback, (ResponseStatus.WRONG_MASTER_PASSWORD, None))
                return
            elif next_step == 3:
                self.app.call_from_thread(result_callback, (ResponseStatus.WRONG_EMAIL, None))
                return
            elif next_step == 4:
                self.app.call_from_thread(result_callback, (ResponseStatus.TIMEOUT, None))
                return
            
            output = child.before
            match = re.search(r'BW_SESSION="([^"]+)"', output)
            if match:
                session_key = match.group(1)
                self.app.call_from_thread(result_callback, (ResponseStatus.SUCCESS, session_key))
                return
            else:
                self.app.call_from_thread(result_callback, (ResponseStatus.UNKNOWN_ERROR, None))
                return
        except pexpect.exceptions.ExceptionPexpect as e:
            self.app.call_from_thread(result_callback, (ResponseStatus.UNKNOWN_ERROR, None))
            return
        finally:
            if child.isalive():
                child.close()
    
    async def get_item(self, item_name: str) -> dict | ResponseStatus:
        """Checks inside the vault and retrieve the inputted item"""
        return await self.client.call("get", "item", item_name)
    
    async def get_token(self, token_name: str) -> dict | ResponseStatus:
        """Seacrh and fetches inputted token"""
        result = await self.get_item(token_name)

        if result == ResponseStatus.ITEM_MISSING:
            return ResponseStatus.PROVIDER_TOKEN_MISSING
        else:
            return result
    
    
    async def unlock(self, password: str) -> ResponseStatus:
        """Unlocks the vault and updates the global session token."""
        result = await self.client.call("unlock", password, "--raw")

        if isinstance(result, ResponseStatus):
            return result
        
        self.app.vault_session = result.strip()
        return ResponseStatus.SUCCESS
  
    
    async def update_provider_token(self, token_name: str, token_value: str) -> ResponseStatus:
        """Explicitly updates the password field of a provider token item."""
        item_json = await self.get_item(token_name)
        
        if isinstance(item_json, ResponseStatus):
            return item_json

        item_json["login"]["password"] = token_value

        encoded_item = json.dumps(item_json)
        result = await self.client.call("edit", "item", item_json["id"], input_data=encoded_item)

        if isinstance(item_json, ResponseStatus):
            return item_json
        
        await self.client.call("sync")
        return ResponseStatus.SUCCESS
        
  