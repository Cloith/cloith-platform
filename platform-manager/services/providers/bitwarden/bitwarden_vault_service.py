import pexpect
import threading
import re
from services import BaseVaultService
from services import VaultStatus
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
                    self.app.call_from_thread(result_callback, (VaultStatus.INVALID_OTP, None))
                    return
                if sub_step == 2:
                    self.app.call_from_thread(result_callback, (VaultStatus.TIMEOUT, None))
                    return

            elif next_step == 2:
                self.app.call_from_thread(result_callback, (VaultStatus.WRONG_PASSWORD, None))
                return
            elif next_step == 3:
                self.app.call_from_thread(result_callback, (VaultStatus.WRONG_EMAIL, None))
                return
            elif next_step == 4:
                self.app.call_from_thread(result_callback, (VaultStatus.TIMEOUT, None))
                return
            
            output = child.before
            match = re.search(r'BW_SESSION="([^"]+)"', output)
            if match:
                session_key = match.group(1)
                self.app.call_from_thread(result_callback, (VaultStatus.SUCCESS, session_key))
                return
            else:
                self.app.call_from_thread(result_callback, (VaultStatus.UNKNOWN_ERROR, None))
                return
        except pexpect.exceptions.ExceptionPexpect as e:
            self.app.call_from_thread(result_callback, (VaultStatus.UNKNOWN_ERROR, None))
            return
        finally:
            if child.isalive():
                child.close()
    
    async def get_item(self, item_name: str) -> dict | str:
        """Checks inside the vault and retrieve the inputted item"""
        return await self.client.call("get", "item", item_name)
    
    async def unlock(self, password: str) -> bool:
        """Unlocks the vault and updates the global session token."""
        result = await self.client.call("unlock", password, "--raw")
        
        if isinstance(result, str) and len(result) > 10: 
            self.app.vault_session = result.strip()
            return VaultStatus.SUCCESS
        return result
    
        
        
    
