from providers.hostinger.client import HostingerClient
from services.base_template import BaseTemplateService

class HostingerTemplateService(BaseTemplateService):
    def __init__(self, client: HostingerClient):
        self.client = client

    async def get_all_templates(self):
        return await self.client.request("GET", "/templates")