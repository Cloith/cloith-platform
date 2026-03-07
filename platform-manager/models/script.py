from dataclasses import dataclass

@dataclass(frozen=True)
class ScriptData:
    id: int  
    name: str
    content: str
    provider: str = "hostinger"