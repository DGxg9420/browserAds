import os
import httpx
import socket
import random
from core.model import ProxyRaw, ProxyProtocolEnum, Proxy
from core.constant import BASE_DIR, CONFIG


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
        with httpx.Client(proxy=proxy_url) as client:
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


def is_port_available(port) -> bool:
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result != 0  # 如果连接失败，说明端口可用


def find_available_port(start_port, end_port) -> int | None:
    """在指定范围内寻找可用端口"""
    while True:
        port = random.randrange(start_port, end_port)
        if is_port_available(port):
            return port


def get_proxy_raw_by_api() -> ProxyRaw | None:
    """通过api获取代理信息"""
    try:
        with httpx.Client() as client:
            response = client.get(CONFIG['proxy']['proxy_get_url'])
            if response.status_code == 200:
                proxy_info = response.text
                if "未加入白名单" in proxy_info:
                    return None
                return ProxyRaw(ip=proxy_info.split(":")[0], port=int(proxy_info.split(":")[1]), protocol=ProxyProtocolEnum.SOCKS5)
            else:
                return None
    except Exception as e:
        print(f"获取代理ip失败：{e!r}")
        return None


if __name__ == '__main__':
    print(find_available_port(8001, 59600))
    # dat = get_proxy_raw_by_api()
    # print(dat)
    # print(is_port_available(9876))