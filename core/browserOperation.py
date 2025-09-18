from DrissionPage import Chromium
from DrissionPage.errors import ElementNotFoundError
from core.constant import BCP_47_LANGS, CONFIG, PLATFORM
from core.utils import generate_32bit_integer, get_proxy_info, get_full_path, find_available_port, is_chrome_debug_ready, delete_all_subdirectories
from core.model import Proxy, ProxyRaw, ProxyProtocolEnum
from core.logger import logger
from traceback import format_exc
from abc import ABC, abstractmethod
from time import sleep
import subprocess
import shutil
import os


class BrowserBase(ABC):
    def __init__(self, proxy_info: Proxy, play_url: str):
        self.play_url: str = play_url
        self.browser_pid: int = 0
        self.browser_port: int = 0
        self.data_path: str = ""
        self.browser: Chromium | None = None
        # 启动浏览器
        self.run_browser(proxy_info=proxy_info)
        self.tab = self.browser.latest_tab

    def __init_browser(self, proxy_info: Proxy):
        result = None
        port = find_available_port(8001, 59600)
        if PLATFORM == "Linux":
            exe_path = CONFIG["browser"]["browser_path_linux_test"]
        elif PLATFORM == "Windows":
            exe_path = CONFIG["browser"]["browser_path_windows_test"]
        else:
            exe_path = CONFIG["browser"]["browser_path"]

        cmd_list = [
            exe_path,
            f"--remote-debugging-port={port}",
        ]
        # 设置浏览器的语言
        try:
            lang_str = BCP_47_LANGS.search(proxy_info.country)
        except AttributeError:
            lang_str = "zh-CN"
        cmd_list.append(f"--lang={lang_str}")
        # 设置浏览器接受的语言
        cmd_list.append(f"--accept-lang={lang_str}")
        # 设置时区
        try:
            timezone = proxy_info.timezone
        except AttributeError:
            timezone = "Asia/Shanghai"
        cmd_list.append(f"--timezone={timezone}")
        # 设置代理
        logger.info(f"使用代理：{proxy_info.proxy_url}")
        cmd_list.append(f"--proxy-server={proxy_info.proxy_url}")
        #  指定指纹种子(seed)
        seed = str(generate_32bit_integer())
        cmd_list.append(f"--fingerprint={seed}")
        # 设置允许自动播放
        cmd_list.append("--autoplay-policy=no-user-gesture-required")
        # 设置数据文件夹
        data_path = get_full_path(os.path.join("browserDatas", seed))
        cmd_list.append("--user-data-dir=" + data_path)
        # 设置静音
        cmd_list.append("--mute-audio")
        # 不加载图片
        cmd_list.append("--blink-settings=imagesEnabled=false")
        # 忽略证书错误
        # cmd_list.append("--ignore-certificate-errors")
        # 默认情况下，https页面不允许从http链接引用javascript / css / plug - ins。添加这一参数会放行这些内容。
        cmd_list.append("--allow-running-insecure-content")
        # 单进程模式
        # cmd_list.append("--single-process")
        #
        cmd_list.append("--no-default-browser-check")
        #
        cmd_list.append("--disable-suggestions-ui")
        #
        cmd_list.append("--no-first-run")
        #
        cmd_list.append("--disable-infobars")
        #
        cmd_list.append("--disable-popup-blocking")
        #
        cmd_list.append("--hide-crash-restore-bubble")
        #
        cmd_list.append("--disable-features=PrivacySandboxSettings4")
        # 无头模式
        cmd_list.append("--headless")

        if PLATFORM == "Linux":
            # 无沙盒模式
            cmd_list.append("--no-sandbox")
            # 禁用GPU
            cmd_list.append("--disable-gpu")

        try:
            result = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.browser_pid = result.pid
            self.browser_port = port
            self.data_path = data_path
            debug_data = is_chrome_debug_ready(port, timeout=15)
            if debug_data and debug_data[0].get("webSocketDebuggerUrl"):
                logger.info(f"使用端口：{port}， 启动浏览器成功！")
                self.browser = Chromium(debug_data[0]["webSocketDebuggerUrl"])
            else:
                raise RuntimeError("浏览器启动失败")
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败！返回码: {e.returncode}\n错误信息: {e.stderr}")
            if result:
                result.kill()
        except Exception as e:
            logger.error(f"启动浏览器错误：{e!r}\n\n{format_exc()}")
            if result:
                result.kill()

    def run_browser(self, proxy_info: Proxy):
        self.__init_browser(proxy_info=proxy_info)

    @abstractmethod
    def startBrowserAds(self) -> bool:
        """
        开始浏览广告逻辑，并返回是否浏览成功
        :return:  返回布尔值
        """
        pass

    def browserClose(self):
        """
        关闭浏览器
        """
        self.browser.quit(del_data=True)
        sleep(3)
        if self.data_path and os.path.exists(self.data_path):
            try:
                shutil.rmtree(self.data_path)
            except Exception as e:
                logger.warning(f"删除数据文件夹失败：{e!r}")


class BrowserOperationOnWebtraficRu(BrowserBase):
    """
    广告网站：https://webtrafic.ru/
    """
    name = "webtrafic.ru"
    def startBrowserAds(self) -> bool:
        try:
            self.tab.get(self.play_url, timeout=60)
            try:
                new_tab = self.tab.ele("#:webtraf").ele("tag:img").click.for_new_tab(by_js=True, timeout=15)
                new_tab.wait.doc_loaded(timeout=60, raise_err=False)
                logger.info(f"访问广告页成功：{new_tab.title}")
            except ElementNotFoundError:
                pass

            return True
        except Exception as e:
            logger.error(f"startBrowserAds Error: {e}\n\n{format_exc()}")
            return False


class BrowserOperation:
    def __init__(self, proxy_info: Proxy, play_url: str, refer_url: str):
        self.play_url: str = play_url
        self.refer_url: str = refer_url
        self.browser_pid: int = 0
        self.browser_port: int = 0
        # 启动浏览器
        self.run_browser(proxy_info=proxy_info)
        self.browser: Chromium = Chromium(f"127.0.0.1:{self.browser_port}")
        self.tab = self.browser.latest_tab

    def run_browser(self, proxy_info: Proxy):
        result = None
        port = 9222
        if PLATFORM == "Linux":
            exe_path = CONFIG["browser"]["browser_path_linux_test"]
        elif PLATFORM == "Windows":
            exe_path = CONFIG["browser"]["browser_path_windows_test"]
        else:
            exe_path = CONFIG["browser"]["browser_path"]

        cmd_list= [
            exe_path,
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
        logger.info(proxy_info.proxy_url)
        cmd_list.append(f"--proxy-server={proxy_info.proxy_url}")
        #  指定指纹种子(seed)
        seed = str(generate_32bit_integer())
        cmd_list.append(f"--fingerprint={seed}")
        # 设置允许自动播放
        cmd_list.append("--autoplay-policy=no-user-gesture-required")
        # 设置数据文件夹
        cmd_list.append("--user-data-dir=" + get_full_path(os.path.join("browserDatas", seed)))
        # 设置静音
        cmd_list.append("--mute-audio")
        # 不加载图片
        cmd_list.append("--blink-settings=imagesEnabled=false")
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
            logger.info("标准输出:", result.stdout)  # 空（因为文件不存在，输出到 stderr）
            logger.info("错误输出:", result.stderr)  # 输出类似: ls: cannot access 'nonexistent_file': No such file or directory
            logger.info(result.pid)
            self.browser_pid = result.pid
            self.browser_port = port
            sleep(3)
        except subprocess.CalledProcessError as e:
            logger.info(f"命令执行失败！返回码: {e.returncode}")
            logger.info("错误信息:", e.stderr)
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
        logger.info(proxy_info.proxy_url)
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
            self.tab.get(self.refer_url)
            logger.info(self.tab.title)
            self.tab.get(self.play_url)
            logger.info(self.tab.user_agent)
            wait_result = self.tab.wait.ele_displayed("@aria-label=Play", raise_err=False)
            if wait_result:
                self.tab.ele("@aria-label=Play").click()
                logger.info("正在播放视频...")
            # aria-label="Replay"
            isPlayEnd = False
            timeout_total = 60 * 7
            logger.info(self.tab.title)
            while not isPlayEnd:
                sleep(1)
                try:
                    isPlayEnd = self.tab.ele("@aria-label=Replay")
                except ElementNotFoundError:
                    isPlayEnd = False
                timeout_total -= 1
                if timeout_total <= 0:
                    logger.info("超时退出！")
                    break
                if timeout_total % 10 == 0:
                    logger.info(f"剩余时间: {timeout_total}s")
                try:
                    result = self.tab.ele("text:This video file cannot be played").states.is_displayed
                    if result:
                        logger.info("视频播放失败！")
                        break
                except ElementNotFoundError:
                    pass
            logger.info("播放结束！")
        except KeyboardInterrupt:
            logger.info("用户退出！")
            raise "用户退出！"


if __name__ == "__main__":
    # 使用示例
    target_directory = "browserDatas"  # 替换为你的目标目录路径
    delete_all_subdirectories(get_full_path(target_directory))
    proxy_info = get_proxy_info(
        ProxyRaw(ip="144.202.17.20", port=7298, protocol=ProxyProtocolEnum.SOCKS5)
    )
    logger.info(proxy_info)
    url = "https://t.co/b7Wfiz9nRV"
    blog_url = "https://ssson966.blogspot.com/2025/09/linuxerror-while-loading-shared.html"

    browser = BrowserOperationOnWebtraficRu(proxy_info=proxy_info, play_url=blog_url)
    try:
        result = browser.startBrowserAds()
        logger.info(result)
        browser.browserClose()
    except Exception as e:
        logger.info(e)
        browser.browserClose()
