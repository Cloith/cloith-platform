from models import ConfigClass
from models import ResponseStatus

class ServiceResponseHandler():
    def __init__(self, app):
        self.app = app

    @property
    def overlay_error_data(self):
        provider = self.app.vps_service.provider_name.title()

        return {
            ResponseStatus.NETWORK_ERROR: {
                "msg": "[bold red]No Internet Connection[/]\n\nPlease check your network and [b blue]Try Again[/]",
                "retry": True
            },
            ResponseStatus.TIMEOUT: {
                "msg": "[bold yellow]Request Timeout[/]\n\nThe service is taking too long to respond\n[b blue]Please Try Again[/]",
                "retry": True
            },
            ResponseStatus.UNKNOWN_ERROR: {
                "msg": "[yellow]Unkown Error[/]\n\nPlease Try Again",
                "retry": True
            },
            ResponseStatus.PROVIDER_TOKEN_MISSING: {
                "msg": (
                    "[b red]Missing Provider Token[/]\n\n\n"
                    f"[b blue]{provider} Token[/] is missing from the vault\n"
                    "Please use [b blue]Create[/] to add your token"
                    ),
                "create": True,
                "mode": "provider"
            },
            ResponseStatus.PROVIDER_TOKEN_INVALID: {
                "msg": (
                    "[b red]Invalid Provider Token[/]\n\n\n"
                    f"Your [b blue]{provider} Token[/] is invalid\n\n"
                    "Please [b green]Update[/] your token"
                    ),
                "update": True,
                "mode": "provider"
            },
            ResponseStatus.INVALID_SESSION_TOKEN: {
                "msg": (
                    "[b red]Invalid Session Token[/]\n\n\n"
                    "Your current[b yellow] Vault Session Token[/] is [b red]invalid[/] or [b red]missing[/]\n\n"
                    "Please [b blue]Auth[/] to continue"
                    ),
                "auth": True,
                "unlock": True
            }
        }

    @property
    def modal_error_data(self):

        return {
            ResponseStatus.NETWORK_ERROR: {
                "msg": "[bold red]No Internet Connection[/]",
                "retry": True,
            },
            ResponseStatus.TIMEOUT: {
                "msg": "[bold yellow]Request Timeout[/]",
                "retry": True
            },
            ResponseStatus.UNKNOWN_ERROR: {
                "msg": "[yellow]Unkown Error[/]",
                "retry": True
            },
            ResponseStatus.PROVIDER_API_ERROR: {
                "msg": f"[b red]API Error[/]",
                "retry": True
            },
            ResponseStatus.PROVIDER_TOKEN_MISSING: {
                "msg": "[b red]Missing Provider Token[/]",
                "create": True
            },
            ResponseStatus.PROVIDER_TOKEN_INVALID: {
                "msg": "[b red]Invalid Provider Token[/]",
                "update": True
            },
            ResponseStatus.INVALID_SESSION_TOKEN: {
                "msg": "[b red]Invalid Session Token[/]",
                "auth": True
            },
            ResponseStatus.WRONG_MASTER_PASSWORD: {
                "msg": "[b red]Master Password is incorrect",
                "unlock": True
            }
        }

    def get_config(self, response: ResponseStatus, type: str) -> ConfigClass:
        error_map = self.modal_error_data if type == "modal" else self.overlay_error_data
        data = error_map.get(response)

        return ConfigClass(
            message=data["msg"],
            mode=data.get("mode", "vault"),
            show_retry=data.get("retry", False),
            show_auth=data.get("auth", False),
            show_unlock=data.get("unlock", False),
            show_update=data.get("update", False),
            show_buy=data.get("buy", False),
            show_create=data.get("create", False),
        )
