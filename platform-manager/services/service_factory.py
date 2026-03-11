from services.base_vps import BaseVPSService
from services.base_vault import BaseVaultService
from providers.hostinger.hostinger_vps_service import HostingerVPSService
from providers.bitwarden.bitwarden_vault_service import BitwardenVaultService

def get_vps_service(provider_name: str, app) -> BaseVPSService:
    if provider_name == "hostinger":
        return HostingerVPSService(app.hostinger_token)
    elif provider_name == "aws":
        raise NotImplementedError("AWS coming soon!")
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

def get_vault_service(provider_name: str, app) -> BaseVaultService:
    if provider_name == "bitwarden":
        return BitwardenVaultService(app)