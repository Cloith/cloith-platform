from abc import ABC, abstractmethod

class BaseVPSService(ABC):
    @abstractmethod
    async def get_all_vps(self) -> list[dict]:
        """Must return a list of VPS objects in a standardized format."""
        pass