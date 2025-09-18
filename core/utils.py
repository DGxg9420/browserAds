import os
import json
import httpx
import socket
import random
from time import time
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


def is_chrome_debug_ready(port: int, timeout: float = 10.0) -> list[dict] | None:
    """
    检测指定端口的 Chrome 远程调试接口是否就绪。

    参数:
        port (int): Chrome 远程调试端口（如 9222）
        timeout (float): 总超时时间（秒），默认 10 秒

    返回:
        bool: 就绪返回 True，否则返回 False
    """
    start_time = time()

    # 步骤1：检查端口是否被监听（TCP 握手）
    while time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(min(1.0, timeout - (time() - start_time)))  # 单次连接超时不超过剩余时间
                s.connect(('localhost', port))
            break  # 端口监听成功，跳出循环
        except (socket.timeout, ConnectionRefusedError):
            continue  # 未监听，继续重试
    else:
        return None  # 总超时未监听到端口

    # 步骤2：验证远程调试接口是否返回有效数据
    http_timeout = max(0.0, timeout - (time() - start_time))  # 剩余可用时间
    if http_timeout <= 0:
        return None

    debug_url = f'http://localhost:{port}/json/list'
    try:
        response = httpx.get(debug_url, timeout=http_timeout)
        if response.status_code != 200:
            return None

        # 解析 JSON 并检查是否包含有效调试目标
        debug_data = response.json()
        if isinstance(debug_data, list) and len(debug_data) > 0:
            # 至少有一个目标包含 WebSocket 调试 URL
            return debug_data
        return None
    except (httpx.RequestError, json.JSONDecodeError):
        return None

if __name__ == '__main__':
    # print(find_available_port(8001, 59600))
    # dat = get_proxy_raw_by_api()
    # print(dat)
    # print(is_port_available(9876))
    print(is_chrome_debug_ready(28397, 15))