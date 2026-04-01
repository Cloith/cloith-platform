from abc import ABC, abstractmethod
from models.vps import VPSData
from enum import IntEnum

class VPSStatus(IntEnum):
    SUCCESS = 1
    TOKEN_MISSING = 2
    TOKEN_INVALID= 3
    TOKEN_MODAL_PROMPT = 4
    INVALID_OTP = 5
    LOCKED = 6
    TIMEOUT = 7
    UNKNOWN_ERROR = 8
    ALREADY_LOGGED_IN = 9
    MASTER_PASSWORD_PROMPT = 10
    ITEM_MISSING = 11
    CANCELLED = 12 

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