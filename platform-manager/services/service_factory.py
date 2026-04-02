from services.base_vps import BaseVPSService
from services.base_vault import BaseVaultService
from services.base_template import BaseTemplateService
from services.providers.hostinger import HostingerVPSService
from services.providers.hostinger import HostingerTemplateService
from services.providers.bitwarden import BitwardenVaultService

def get_vps_service(provider_name: str, app) -> BaseVPSService:
    if provider_name == "hostinger":
        return HostingerVPSService(app)
    elif provider_name == "aws":
        raise NotImplementedError("AWS coming soon!")
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def get_vault_service(provider_name: str, app) -> BaseVaultService:
    if provider_name == "bitwarden":
        return BitwardenVaultService(app)
    
def get_template_service(provider_name: str, app) -> BaseTemplateService:
    if provider_name == "hostinger":
        return HostingerTemplateService(app)