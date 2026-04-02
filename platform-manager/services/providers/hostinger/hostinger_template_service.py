from services.providers.hostinger import HostingerClient
from services import BaseTemplateService

class HostingerTemplateService(BaseTemplateService):
    def __init__(self, app):
        self.app = app
        self.client = HostingerClient(app)

    @property
    def provider_name(self) -> str:
        return "hostinger"
    
    async def get_all_templates(self):
        return await self.client.request("GET", "/templates")