import httpx
from services.base_vps import VPSStatus

class HostingerClient:
    def __init__(self, app):
        self.app = app
        self.base_url = "https://developers.hostinger.com/api/vps/v1"

    async def request(self, method: str, endpoint: str, **kwargs):
        """Centralized request handler with error handling."""
        if not self.app.provider_token:
            return VPSStatus.TOKEN_MISSING
        
        url = f"{self.base_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {self.app.provider_token}",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=headers, timeout=10, **kwargs)
            
            if response.status_code == 401:
                return VPSStatus.TOKEN_INVALID
  
            return response.json()