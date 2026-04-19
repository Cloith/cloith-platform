from custom_widgets import OverlayConfig
from models.status import ResponseStatus

class ClientRequestHandler:

    def get_config(self, response: ResponseStatus):

        if response == ResponseStatus.NETWORK_ERROR:
            config = OverlayConfig(
                message="[red]No Internet Connection[/]\n\nPlease check your network and try again.",
                show_retry=True
            )
            return config
        elif response == ResponseStatus.TIMEOUT:
            config = OverlayConfig(
                message="[yellow]Request Timed Out[/]\n\nHostinger is taking too long to respond.",
                show_retry=True
            )
            return config
        elif response == ResponseStatus.UNKNOWN_ERROR:
            config = OverlayConfig(
                message="[yellow]Unkown Error[/]\n\nPlease Try Again",
                show_retry=True
            )
            return config
        elif response == ResponseStatus.MASTER_PASSWORD_PROMPT:
            config = OverlayConfig(
                message="""[red]Authentication Required[/] \n\n Something went wrong while accessing your vault.\n Please [blue]authorize[/] to continue.""",
                show_auth=  True
                )
            return config
        elif response == ResponseStatus.ITEM_MISSING:
            config = OverlayConfig(
                message=f"[red]Missing Vault Item[/]\n\n We couldn't find item in your vault.\n Please [blue]authorize[/] a new token.",
                mode="provider", 
                show_auth=True
            )
            return config
        elif response == ResponseStatus.TOKEN_INVALID:
            config = OverlayConfig(
                message=f"""Your [bold orange]{self.app.vps_service.provider_name.title()} token[/] is [red]invalid[/]\n\n\n Please [blue]authorize[/] to continue.""",
                mode="provider",
                show_auth=True
            )
            return config
        elif response == ResponseStatus.TOKEN_MISSING:
            config = OverlayConfig(
                message = f"""[red]Missing Token[/]\n\n [green]{self.app.vps_service.provider_name.title()} token[/] is [red]missing from vault[/]\n\n\n"""
            )
            return config