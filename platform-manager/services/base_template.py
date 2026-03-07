from abc import ABC, abstractmethod

class BaseTemplateService(ABC):
    @abstractmethod
    async def get_all_templates(self):
        """Must return a list of VPS objects in a standardized format."""
        pass 