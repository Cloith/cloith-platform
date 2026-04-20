from services.base_provider import BaseProviderService
from services.base_vault import BaseVaultService
from services.providers.hostinger import HostingerProviderService
from services.providers.bitwarden import BitwardenVaultService

def get_provider_service(provider_name: str, app) -> BaseProviderService:
    if provider_name == "hostinger":
        return HostingerProviderService(app)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def get_vault_service(provider_name: str, app) -> BaseVaultService:
    if provider_name == "bitwarden":
        return BitwardenVaultService(app)
    
