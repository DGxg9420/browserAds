from DrissionPage import ChromiumOptions, Chromium
from DrissionPage.errors import ElementNotFoundError
from core.constant import BCP_47_LANGS, CONFIG, PLATFORM
from core.utils import generate_32bit_integer, get_proxy_info, get_full_path
from core.model import Proxy, ProxyRaw, ProxyProtocolEnum
from time import sleep
import subprocess



class BrowserOperation:
    def __init__(self, proxy_info: Proxy, play_url: str):
        self.play_url = play_url
        self.browser_pid: int = 0
        self.browser_port: int = 0
        # 启动浏览器
        self.run_browser(proxy_info=proxy_info)
        self.browser: Chromium = Chromium(f"127.0.0.1:{self.browser_port}")
        self.tab = self.browser.latest_tab

    def run_browser(self, proxy_info: Proxy):
        result = None
        port = 9222
        cmd_list= [
            CONFIG["browser"]["browser_path_windows_test"],
            f"--remote-debugging-port={port}",
        ]
        # 设置浏览器的语言
        lang_str = BCP_47_LANGS.search(proxy_info.country)
        cmd_list.append(f"--lang={lang_str}")
        # 设置浏览器接受的语言
        cmd_list.append(f"--accept-lang={lang_str}")
        # 设置时区
        cmd_list.append(f"--timezone={proxy_info.timezone}")
        # 设置代理
        print(proxy_info.proxy_url)
        cmd_list.append(f"--proxy-server={proxy_info.proxy_url}")
        #  指定指纹种子(seed)
        seed = str(generate_32bit_integer())
        cmd_list.append(f"--fingerprint={seed}")
        # 设置允许自动播放
        cmd_list.append("--autoplay-policy=no-user-gesture-required")
        # 设置数据文件夹
        cmd_list.append(get_full_path(f"browserDatas/{seed}"))
        if PLATFORM == "Linux":
            # 无沙盒模式
            cmd_list.append("--no-sandbox")
            # 禁用GPU
            cmd_list.append("--disable-gpu")
            # 无头模式
            cmd_list.append("--headless")

        try:
            result = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            print("标准输出:", result.stdout)  # 空（因为文件不存在，输出到 stderr）
            print("错误输出:", result.stderr)  # 输出类似: ls: cannot access 'nonexistent_file': No such file or directory
            print(result.pid)
            self.browser_pid = result.pid
            self.browser_port = port
            sleep(3)
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败！返回码: {e.returncode}")
            print("错误信息:", e.stderr)
            if result:
                result.kill()

    def __config_browser(self, proxy_info: Proxy):
        # 设置不加载图片、静音
        # self.co.no_imgs(True).mute(True)
        # 无头模式
        self.co.headless(True)
        self.co.set_argument("--disable-gpu")
        # 设置浏览器的语言
        lang_str = BCP_47_LANGS.search(proxy_info.country)
        self.co.set_argument("--lang", lang_str)
        # 设置浏览器接受的语言
        self.co.set_argument("--accept-lang", lang_str)
        # 设置端口
        self.co.auto_port(True)
        # 设置时区
        self.co.set_argument("--timezone", proxy_info.timezone)
        # 设置代理
        print(proxy_info.proxy_url)
        self.co.set_argument("--proxy-server", proxy_info.proxy_url)
        #  指定指纹种子(seed)
        seed = str(generate_32bit_integer())
        self.co.set_argument("--fingerprint", seed)
        # 设置允许自动播放
        self.co.set_argument("--autoplay-policy", "no-user-gesture-required")
        # 设置数据文件夹
        # self.co.set_user_data_path(f"browserDatas/{seed}")
        # 无沙盒模式
        self.co.set_argument("--no-sandbox")
        # 设置浏览器路径
        self.co.set_browser_path(
            r"/root/ungoogled-chromium-139.0.7258.154-1-x86_64_linux/chrome"
        )

    def play_video(self):
        try:
            self.tab.get(self.play_url)
            wait_result = self.tab.wait.ele_displayed("@aria-label=Play", raise_err=False)
            if wait_result:
                self.tab.ele("@aria-label=Play").click()
                print("正在播放视频...")
            # aria-label="Replay"
            isPlayEnd = False
            timeout_total = 60 * 7
            print(self.tab.title)
            while not isPlayEnd:
                sleep(1)
                try:
                    isPlayEnd = self.tab.ele("@aria-label=Replay")
                except ElementNotFoundError:
                    isPlayEnd = False
                timeout_total -= 1
                if timeout_total <= 0:
                    print("超时退出！")
                    break
                if timeout_total % 10 == 0:
                    print(f"剩余时间: {timeout_total}s")
                try:
                    self.tab.ele("text:This video file cannot be played")
                    print("视频播放失败！")
                    break
                except ElementNotFoundError:
                    pass
            print("播放结束！")
        except KeyboardInterrupt:
            print("用户退出！")
            raise "用户退出！"


if __name__ == "__main__":
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
