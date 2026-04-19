from models import OverlayConfig
from models import ResponseStatus

class ClientRequestHandler:

    def get_config(self, response: ResponseStatus):

        if response == ResponseStatus.NETWORK_ERROR:
            config = OverlayConfig(
                message="[bold red]No Internet Connection[/]\n\nPlease check your network and try again.",
                show_retry=True
            )
            return config
        elif response == ResponseStatus.TIMEOUT:
            config = OverlayConfig(
                message="[bold yellow]Request Timed Out[/]",
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
                show_auth=  True,
                show_unlock=True
                )
            return config
        elif response == ResponseStatus.ITEM_MISSING:
            config = OverlayConfig(
                message=f"[red]Missing Vault Item[/]\n\n We couldn't find item in your vault.\n Please [blue]authorize[/] a new token.",
                mode="provider", 
                show_auth=True,
                show_unlock=True
            )
            return config
        elif response == ResponseStatus.TOKEN_INVALID:
            config = OverlayConfig(
                message=f"""Your [bold orange]{self.app.vps_service.provider_name.title()} token[/] is [red]invalid[/]\n Please [blue]update[/] your token to continue.""",
                mode="provider",
                show_update=True
            )
            return config
        elif response == ResponseStatus.TOKEN_MISSING:
            config = OverlayConfig(
                message = f"""[green]{self.app.vps_service.provider_name.title()} token[/] is [red]missing from vault[/]\n\n\n Please go to the secret manager to create the token""",
                show_secret_manager=True
            )
            return config
        elif response == ResponseStatus.WRONG_MASTER_PASSWORD:
            config = OverlayConfig(
                message = f"""[bold orange]Master Password[/] is [red]incorrect[/]""",
                show_unlock=True,
            )
            return config