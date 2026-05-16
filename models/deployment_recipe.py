from dataclasses import dataclass, field

@dataclass
class DeploymentRecipe:
    provider: str = ""
    vps_id: str = ""
    template_id: str = ""
    root_password: str = ""
    panel_password: str = ""
    scripts: list = field(default_factory=list)
    is_ready: bool = False

    @property
    def has_provider(self) -> bool:
        """Returns True if a provider is selected."""
        return bool(self.provider)