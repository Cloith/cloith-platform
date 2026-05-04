import pexpect
import json
import threading
import logging
import re
from models import ResponseStatus
from services import BaseVaultService
from services.vaults.bitwarden import BitwardenClient

class BitwardenVaultService(BaseVaultService):
    logging.basicConfig(
        filename='/workspaces/cloith-platform/platform.log',
        level=logging.INFO,
        format='%(message)s'
    )
    
    def __init__(self, app):
        self.app = app
        self.client = BitwardenClient(app)
    
    @property
    def provider_name(self) -> str:
        return "bitwarden"
    
    async def get_item(self, *args: str) -> dict | ResponseStatus:
        """Checks inside the vault and retrieve the inputted item"""
        return await self.client.call("get", *args)
        
    async def get_item_template(self):
        result = await self.get_item("template", "item")
        
    async def get_folder(self, name: str):
        result = await self.get_item("folder", name)
        result = result.get("id")
        
        result = await self.client.call("list", "items", "--folderid", result)
        logging.info(f"{result}")
        return result
        # logging.info(f"{json.dumps(result, indent=2)}")
        # logging.info(f"{result}")

    async def unlock(self, password: str) -> ResponseStatus:
        """Unlocks the vault and updates the global session token."""
        result = await self.client.call("unlock", password, "--raw")

        if isinstance(result, ResponseStatus):
            return result
        self.app.vault_session = result.strip()

        return ResponseStatus.SUCCESS
    
    async def encode_data(self, item_json: dict, token_value:str) -> str:
        """Encode an edited json for bitwarden input"""
        item_json["login"]["password"] = token_value
        edited_json = json.dumps(item_json)
    
        return await self.client.call("encode", input_data=edited_json)
    
    async def update_provider_token(self, token_value: str) -> ResponseStatus:
        """Explicitly updates the password field of a provider token item with auto verification"""
        original_token = self.app.provider_token
        self.app.provider_token = token_value

        check_result = await self.app.provider_service.check_token()
        if check_result is not ResponseStatus.SUCCESS:
            self.app.provider_token = original_token
            return check_result
        
        token_name = f"{self.app.provider_service.provider_name}_token"
        item_json = await self.get_token(token_name)
        if isinstance(item_json, ResponseStatus):
            return item_json
        
        encoded_string = await self.encode_data(item_json, token_value)
        
        if isinstance(encoded_string, ResponseStatus):
            return encoded_string
        
        edit_result = await self.client.call("edit", "item", item_json["id"], encoded_string)

        if isinstance(edit_result, ResponseStatus):
            return edit_result
        
        sync_result = await self.client.call("sync")

        if isinstance(sync_result, ResponseStatus):
                return sync_result
        
        return ResponseStatus.SUCCESS
    

    
    async def ensure_vault_folders(self):
        required_folders = [
            "platform-manager",
            "platform-manager/tokens",
            "platform-manager/scripts",
            "platform-manager/recipes"
        ]
        
        existing_folders = await self.client.call("list", "folders")
        target_name = "cloith-platform/tokens"

        folder_id = next((f['id'] for f in existing_folders if f['name'] == target_name), None)

        result = await self.client.call("get", "folder", folder_id)
        
        

        self.app.notify(f"{result}")
    #     # existing_names = {f.name: f.id for f in existing_folders}
        
    #     # for path in required_folders:
    #     #     if path not in existing_names:
    #     #         self.app.notify(f"Initializing: {path}", severity="information")
    #     #         new_folder = await self.client.call("create", "folder", path)
    #     #         existing_names[path] = new_folder.id
                
    #     # return existing_names 


  