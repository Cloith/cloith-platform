from abc import ABC, abstractmethod

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
    async def get_token(self, item_name: str) -> dict | str:
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
    