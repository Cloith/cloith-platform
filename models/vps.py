from dataclasses import dataclass
from typing import Optional

@dataclass
class VPSData:
    id: str
    name: str
    status: str
    ip: str
    cpu_cores: int
    ram_gb: float
    disk_gb: float
    os_name: str
    description: str
    provider: str  
    raw_data: Optional[dict] = None  