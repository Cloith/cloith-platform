from services.base_service import BaseVPSService
from providers.hostinger.api import HostingerClient

class HostingerVPSService(BaseVPSService):
    def __init__(self, client: HostingerClient):
        self.client = client

    async def get_all_vps(self):
        raw_data = await self.client.request("GET", "/virtual-machines")
        return [{"id": v["id"], "name": v["name"], "status": v["status"]} for v in raw_data]
