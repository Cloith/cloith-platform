from services.base_vps import BaseVPSService
from services.base_vault import BaseVaultService
from services.base_template import BaseTemplateService
from services.providers.hostinger import HostingerService
from services.providers.bitwarden import BitwardenVaultService

def get_provider_service(provider_name: str, app) -> BaseVPSService:
    if provider_name == "hostinger":
        return HostingerService(app)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def get_vault_service(provider_name: str, app) -> BaseVaultService:
    if provider_name == "bitwarden":
        return BitwardenVaultService(app)
    
