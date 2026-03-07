from services.base_vps import BaseVPSService
from providers.hostinger.vps_service import HostingerVPSService

def get_vps_service(provider_name: str, app) -> BaseVPSService:
    if provider_name == "hostinger":
        return HostingerVPSService(app.hostinger_token)
    elif provider_name == "aws":
        raise NotImplementedError("AWS coming soon!")
    else:
        raise ValueError(f"Unknown provider: {provider_name}")