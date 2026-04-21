from abc import ABC, abstractmethod
from models.vps import VPSData

class BaseProviderService(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Must Returns the name of the provider for UI labels."""
        pass

    @abstractmethod
    async def get_all_vps(self) -> list[VPSData]:
        """Must return a list of VPS objects in a standardized format."""
        pass 