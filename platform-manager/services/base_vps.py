from abc import ABC, abstractmethod
from models.vps import VPSData
from enum import Enum

class VPSStatus(str, Enum):
    SUCCESS = "success"
    TOKEN_MISSING = "token_missing"
    TOKEN_INVALID = "token_invalid"
    TOKEN_MODAL_PROMPT = "token_modal_prompt"
    INVALID_OTP = "invalid_otp"
    LOCKED = "locked"
    TIMEOUT = "timeout"
    UNKNOWN_ERROR = "unknown_error"
    ALREADY_LOGGED_IN = "already_logged_in"
    MASTER_PASSWORD_PROMPT = "master_password_prompt"
    ITEM_MISSING = "item_missing"
    CANCELLED = "cancelled"

class BaseVPSService(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the provider for UI labels."""
        pass

    @abstractmethod
    async def get_all_vps(self) -> list[VPSData]:
        """Must return a list of VPS objects in a standardized format."""
        pass 