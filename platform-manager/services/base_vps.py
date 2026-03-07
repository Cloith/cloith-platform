from abc import ABC, abstractmethod
from models.vps import VPSData

class BaseVPSService(ABC):
    @abstractmethod
    async def get_all_vps(self) -> list[VPSData]:
        """Must return a list of VPS objects in a standardized format."""
        pass 