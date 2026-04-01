from services.base_vps import BaseVPSService
from providers.hostinger.hostinger_client import HostingerClient
from models.vps import VPSData
from services.base_vps import VPSStatus
from services.base_vault import VaultStatus

class HostingerVPSService(BaseVPSService):
    def __init__(self, app):
        self.app = app
        self.client = HostingerClient(app)

    @property
    def provider_name(self) -> str:
        return "hostinger"

    async def get_all_vps(self) -> list[VPSData]:
        result = await self.client.request("GET", "/virtual-machines")

        if result == VPSStatus.TOKEN_MISSING: return result
        elif result == VPSStatus.TOKEN_INVALID: return result

        vps_objects = []
        for v in result:
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
    
        
