import httpx 

class HostingerClient:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://developers.hostinger.com/api/vps/v1"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    async def request(self, method: str, endpoint: str, **kwargs):
        """Centralized request handler with error handling."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()