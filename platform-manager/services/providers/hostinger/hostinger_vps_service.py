from services.base_vps import BaseVPSService
from services.providers.hostinger import HostingerClient
from models.vps import VPSData
from models.status import ResponseStatus
from custom_widgets import OverlayConfig

class HostingerVPSService(BaseVPSService):
    def __init__(self, app):
        self.app = app
        self.client = HostingerClient(app)

    @property
    def provider_name(self) -> str:
        return "hostinger"

    async def get_all_vps(self) -> list[VPSData]:
        result = await self.client.request("GET", "/virtual-machines")

        if not isinstance(result, OverlayConfig):
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
        else:
            return result
    
    async def check_token(self, token_value: str) -> ResponseStatus:
        """Validates the token and updates the app state if successful."""

        original_token = self.app.provider_token
        self.app.provider_token = token_value
        
        result = await self.client.request("GET", "/virtual-machines")

        if not isinstance(result, OverlayConfig):
            token_name = f"{self.app.vps_service.provider_name}_token"
            result =  await self.app.vault_service.update_provider_token(token_name, token_value)

            if not (result, OverlayConfig):
                return ResponseStatus.SUCCESS
            else:
                return result
        else:
            self.app.provider_token = original_token
            return result
            

    
        
