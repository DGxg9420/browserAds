from DrissionPage import ChromiumOptions, Chromium
from core.constant import BCP_47_LANGS
from core.utils import generate_32bit_integer, get_proxy_info
from core.model import Proxy, ProxyRaw, ProxyProtocolEnum


class BrowserOperation:
    def __init__(self, proxy_info: Proxy):
        self.co: ChromiumOptions = ChromiumOptions()
        # 配置浏览器
        self.__config_browser(proxy_info=proxy_info)

        self.browser: Chromium = Chromium(self.co)

        self.tab = self.browser.latest_tab


    def __config_browser(self, proxy_info: Proxy):
        # 设置不加载图片、静音
        # self.co.no_imgs(True).mute(True)
        # 无头模式
        # self.co.headless()
        # 设置浏览器的语言
        lang_str = BCP_47_LANGS.search(proxy_info.country)
        self.co.set_argument('--lang', lang_str)
        # 	设置浏览器接受的语言
        self.co.set_argument('--accept-lang', lang_str)
        # 设置时区
        self.co.set_argument('--timezone', proxy_info.timezone)
        # 	设置代理
        self.co.set_argument('--proxy-server', proxy_info.proxy_url)
        #  指定指纹种子(seed)
        seed = str(generate_32bit_integer())
        self.co.set_argument('--fingerprint', seed)
        # 设置允许自动播放
        self.co.set_argument('--autoplay-policy', "no-user-gesture-required")
        # 设置数据文件夹
        self.co.set_user_data_path(f"browserDatas/{seed}")
        # 设置浏览器路径
        self.co.set_browser_path(r"E:\fingerprintbrowser\ungoogled-chromium_139.0.7258.154-1.1_windows_x64\chrome.exe")

    def play_video(self):
        self.tab.get("https://t.co/BAgdHQwOk0")
        wait_result = self.tab.wait.ele_displayed('@aria-label=Play', raise_err=False)
        if wait_result:
            self.tab.ele('@aria-label=Play').click()
        print(self.tab.title)


if __name__ == '__main__':
    proxy_info = get_proxy_info(ProxyRaw(ip="66.42.224.229", port=41679, protocol=ProxyProtocolEnum.SOCKS5))
    print(proxy_info)
    browser = BrowserOperation(proxy_info=proxy_info)
    print(browser.browser.tabs_count)
    browser.play_video()
    browser.browser.quit()