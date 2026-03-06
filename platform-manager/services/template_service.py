from providers.hostinger.api import HostingerClient

class HostingerTemplateService:
    def __init__(self, client: HostingerClient):
        self.client = client

    async def get_all_templates(self):
        return await self.client.request("GET", "/templates")