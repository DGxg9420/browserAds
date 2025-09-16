import os
import httpx
import random
from core.model import ProxyRaw, ProxyProtocolEnum, Proxy
from core.constant import BASE_DIR


def generate_32bit_integer() -> int:
    """生成一个随机的32位有符号整数"""
    return random.randint(-0x80000000, 0x7FFFFFFF)


async def get_proxy_info_async(proxy_raw: ProxyRaw) -> Proxy | None:
    """获取代理信息"""
    url = "https://ipinfo.io/json"
    auth_info = proxy_raw.username + ":" + proxy_raw.password + "@" if proxy_raw.username else ""
    proxy_url = f"{proxy_raw.protocol.SOCKS5.value}://{auth_info}{proxy_raw.ip}:{proxy_raw.port}"
    try:
        async with httpx.AsyncClient(proxy=proxy_url, verify=False) as client:
            response = await client.get(url, timeout=10)
            proxy_info_dict = proxy_raw.model_dump()
            proxy_info_dict.update(response.json())
            return Proxy(**proxy_info_dict)
    except Exception as e:
        print(e)
        return  None


def get_proxy_info(proxy_raw: ProxyRaw) -> Proxy | None:
    """获取代理信息"""
    url = "https://ipinfo.io/json"
    auth_info = proxy_raw.username + ":" + proxy_raw.password + "@" if proxy_raw.username else ""
    proxy_url = f"{proxy_raw.protocol.SOCKS5.value}://{auth_info}{proxy_raw.ip}:{proxy_raw.port}"
    try:
        with httpx.Client(proxy=proxy_url, verify=False) as client:
            response = client.get(url, timeout=10)
            proxy_info_dict = proxy_raw.model_dump()
            proxy_info_dict.update(response.json())
            proxy_info_dict["proxy_url"] = proxy_url
            return Proxy(**proxy_info_dict)
    except Exception as e:
        print(e)
        return  None

def get_full_path(_path: str) -> str:
    return os.path.join(BASE_DIR, _path)


if __name__ == '__main__':
    import asyncio
    data = asyncio.run(get_proxy_info_async(ProxyRaw(ip="66.42.224.229", port=41679, protocol=ProxyProtocolEnum.SOCKS5)))
    print(data)
