from pydantic import BaseModel
from typing import Optional
from enum import Enum


class ProxyProtocolEnum(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"
    SOCKS4 = "socks4"


class ProxyRaw(BaseModel):
    ip: str
    port: int
    username: Optional[str] = None
    password:  Optional[str] = None
    protocol: ProxyProtocolEnum = ProxyProtocolEnum.SOCKS5


class Proxy(ProxyRaw):
    city: str
    region: str
    country: str
    timezone: str
    proxy_url: str