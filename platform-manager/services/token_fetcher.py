class VaultService:
    def __init__(self, storage_path: str = "vault.json"):
        self.storage_path = storage_path

    def get_secret(self, key: str) -> str | None:
        # 1. Check memory/cache
        # 2. Check environment variables (e.g., os.getenv(key))
        # 3. Check local vault.json file
        return "some_token"

    def save_secret(self, key: str, value: str):
        # Save to vault.json so it's there when the app restarts
        pass