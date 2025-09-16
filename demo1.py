from  core.utils import get_proxy_info
from core.model import ProxyRaw, ProxyProtocolEnum
from core.browserOperation import BrowserOperation

proxy_info = get_proxy_info(
        ProxyRaw(ip="174.64.199.82", port=4145, protocol=ProxyProtocolEnum.SOCKS5)
    )
print(proxy_info)
url = "https://t.co/b7Wfiz9nRV"
browser = BrowserOperation(proxy_info=proxy_info, play_url=url)
try:
    print(browser.browser.tabs_count)
    browser.play_video()
except Exception as e:
    print(e)
finally:
    browser.browser.quit()