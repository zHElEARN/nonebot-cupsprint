from pydantic import BaseModel
from typing import List, Optional


class ScopedConfig(BaseModel):
    group_whitelist: Optional[List[str]] = None
    private_whitelist: Optional[List[str]] = None

    group_blacklist: Optional[List[str]] = None
    private_blacklist: Optional[List[str]] = None

    printer_name: Optional[str] = None
    scanner_name: Optional[str] = None

    scan_resolution: int = 300
    scan_mode: str = "Color"


class Config(BaseModel):
    cupsprint: ScopedConfig = ScopedConfig()
