import httpx
from models.status import ResponseStatus

class HostingerClient:
    def __init__(self, app):
        self.app = app
        self.base_url = "https://developers.hostinger.com/api/vps/v1"

    async def request(self, method: str, endpoint: str, **kwargs):
        if not self.app.provider_token:
            token_name = f"{self.app.vps_service.provider_name}_token"
            vault_res = await self.app.vault_service.get_token(token_name)
            if isinstance(vault_res, dict):
                self.app.provider_token = vault_res.get("login", {}).get("password")
                return await self.request(method, endpoint, **kwargs)
        
            return vault_res
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.app.provider_token}",
            "Accept": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, headers=headers, timeout=10, **kwargs)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    response =  ResponseStatus.PROVIDER_TOKEN_INVALID
                elif response.status_code >= 400:
                    response =  ResponseStatus.PROVIDER_API_ERROR

        except httpx.TimeoutException:
            response =  ResponseStatus.TIMEOUT
        except httpx.NetworkError:
            response =  ResponseStatus.NETWORK_ERROR
        except Exception:
            response =  ResponseStatus.UNKNOWN_ERROR
        return response