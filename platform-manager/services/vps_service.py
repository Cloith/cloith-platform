from services.base_service import BaseVPSService
from providers.hostinger.api import HostingerClient
from models.vps import VPSData

class HostingerVPSService(BaseVPSService):
    def __init__(self, client: HostingerClient):
        self.client = client

    async def get_all_vps(self) -> list[dict]:
        raw_data = await self.client.request("GET", "/virtual-machines")
        
        vps_objects = []
        for v in raw_data:
            vps_objects.append(VPSData(
                id=str(v.get("id")),
                name=v.get("hostname", "Unknown"),
                status=v.get("state", "unknown").upper(),
                ip=(v.get("ipv4") or [{}])[0].get("address", "N/A"),
                cpu_cores=v.get("cpus", 0),
                ram_gb=v.get("memory", 0) / 1024,
                disk_gb=v.get("disk", 0) / 1024,
                os_name=v.get("template", {}).get("name", "N/A"),
                description=v.get("template", {}).get("description", ""),
                provider="hostinger",
                raw_data=v 
            ))
        return vps_objects