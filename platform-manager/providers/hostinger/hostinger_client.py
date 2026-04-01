import httpx
from services.base_vps import VPSStatus

class HostingerClient:
    def __init__(self, app):
        self.app = app
        self.base_url = "https://developers.hostinger.com/api/vps/v1"
        self.headers = {"Authorization": f"Bearer {self.app.provider_token}"}

    async def request(self, method: str, endpoint: str, **kwargs):
        """Centralized request handler with error handling."""
        if self.app.provider_token is None or self.app.provider_token == "":
            return VPSStatus.TOKEN_MISSING
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, timeout=10, **kwargs)
            
            if response.status_code == 401:
                return VPSStatus.TOKEN_INVALID
            #     # 1. Trigger the 'Re-Authenticate' workflow
            #     # This might pop up the Modal or re-fetch from Bitwarden
            #     new_token = await self.trigger_token_refresh() 
                
            #     # 2. Update the headers for this client instance
            #     self.token = new_token
            #     self.headers["Authorization"] = f"Bearer {new_token}"
                
            #     # 3. RETRY the request one more time with the new token
            #     return await self.request(method, endpoint, **kwargs)

            # response.raise_for_status()
            return response.json()