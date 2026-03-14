import pexpect
import threading
import re
from services.base_vault import BaseVaultService
from services.base_vault import AuthStatus
from providers.bitwarden.bitwarden_client import BitwardenClient

class BitwardenVaultService(BaseVaultService):
    def __init__(self, app):
        self.app = app
        self._otp_event = threading.Event()
        self.client = BitwardenClient(app)
        

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
                    self.app.call_from_thread(result_callback, (AuthStatus.INVALID_OTP, None))
                    return
                if sub_step == 2:
                    self.app.call_from_thread(result_callback, (AuthStatus.TIMEOUT, None))
                    return

            elif next_step == 2:
                self.app.call_from_thread(result_callback, (AuthStatus.WRONG_PASSWORD, None))
                return
            elif next_step == 3:
                self.app.call_from_thread(result_callback, (AuthStatus.WRONG_EMAIL, None))
                return
            elif next_step == 4:
                self.app.call_from_thread(result_callback, (AuthStatus.TIMEOUT, None))
                return
            
            output = child.before
            match = re.search(r'BW_SESSION="([^"]+)"', output)
            if match:
                session_key = match.group(1)
                self.app.call_from_thread(result_callback, (AuthStatus.SUCCESS, session_key))
                return
            else:
                self.app.call_from_thread(result_callback, (AuthStatus.UNKNOWN_ERROR, None))
                return
        except pexpect.exceptions.ExceptionPexpect as e:
            self.app.call_from_thread(result_callback, (AuthStatus.UNKNOWN_ERROR, None))
            return
        finally:
            if child.isalive():
                child.close()
    
    async def get_secrets(self, item_name: str) -> dict | str:
        return await self.client.call("get", "item", item_name)
    
        
        
    
