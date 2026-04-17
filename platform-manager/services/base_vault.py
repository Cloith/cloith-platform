from abc import ABC, abstractmethod
from enum import Enum

class VaultStatus(str, Enum):
    SUCCESS = "success"
    NEED_2FA = "need_2fa"
    WRONG_PASSWORD = "wrong_password"
    WRONG_EMAIL = "wrong_email"
    INVALID_OTP = "invalid_otp"
    LOCKED = "locked"
    TIMEOUT = "timeout"
    UNKNOWN_ERROR = "unknown_error"
    ALREADY_LOGGED_IN = "already_logged_in"
    MASTER_PASSWORD_PROMPT = "master_password_prompt"
    ITEM_MISSING = "item_missing"
    CANCELLED = "cancelled"
    

class BaseVaultService(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the provider for UI labels."""
        pass

    @abstractmethod
    def run_login_thread(self, email: str, password: str, otp_callback: callable, result_callback: callable) -> None:
        """
        Starts a thread for the vault_login method
        """
        pass

    @abstractmethod
    def vault_login(self, email: str, password: str, otp_callback: callable, result_callback: callable) -> tuple[int, str | None]:
        """
        Handles the pexpect-based login conversation.
        Returns (status_code, session_token).
        """
        pass

    @abstractmethod
    async def get_item(self, item_name: str) -> dict | str:
        pass

    # @abstractmethod
    # async def unlock(self, key: str) -> bool:
    #     """Opens the vault using the provided secret/password."""
    #     pass


    # @abstractmethod
    # async def get_secret(self, identifier: str) -> str:
    #     """Retrieves a specific secret string."""
    #     pass

    # @abstractmethod
    # async def sync(self) -> None:
    #     """Synchronizes local data with the provider (The 'Sync' command)."""
    #     pass
    