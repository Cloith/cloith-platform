from services.vaults.bitwarden import BitwardenClient
from core.handlers import ResponseStatus

class BitwardenTokenService:
    def __init__(self, app):
        self.app = app
        self.client = BitwardenClient(app)
        
    async def get_token(self, token_name: str) -> dict | ResponseStatus:
        """Seacrh and fetches inputted token"""
        result = await self.get_item("item", token_name)
        
        if result == ResponseStatus.ITEM_MISSING:
            return ResponseStatus.PROVIDER_TOKEN_MISSING
        else:
            return result
        