from  core.utils import get_proxy_info
from core.browserOperation import BrowserOperationOnWebtraficRu
from core.constant import PLATFORM
from core.utils import get_proxy_raw_by_api
from concurrent.futures import ThreadPoolExecutor
from queue import Queue


def run_browser_operation(_result_queue: Queue, _run_state: dict[str, bool], _blog_url: str):
    while True:
        if not _run_state["state"]:
            break
        proxy_raw = get_proxy_raw_by_api()
        if not proxy_raw:
            print("没有可用的代理")
            continue
        proxy_info = get_proxy_info(proxy_raw)
        if not proxy_info:
            print("代理信息获取失败")
            continue

        browser_operation = BrowserOperationOnWebtraficRu(proxy_info=proxy_info, play_url=_blog_url)
        try:
            result = browser_operation.startBrowserAds()
            print(result)
            _result_queue.put(result)
            browser_operation.browserClose()
        except Exception as e:
            print(e)
            _result_queue.put(False)
            browser_operation.browserClose()


def count_success_count(_result_queue: Queue, length: int=100):
    success_count = 0
    while True:
        if success_count >= length:
            print("\n任务完成！")
            run_state["state"] = False
            break
        result = _result_queue.get()
        if result:
            success_count += 1
            print(f"\r成功次数：{success_count}", end="")


if __name__ == '__main__':
    run_state: dict[str, bool] = {"state": True}
    result_queue: Queue[bool] = Queue()
    blog_url = "https://ssson966.blogspot.com/2025/09/linuxerror-while-loading-shared.html"
    if PLATFORM == "Windows":
        thread_num = 20
    else:
        thread_num = 10
    browser_count = 10000
    with ThreadPoolExecutor(max_workers=thread_num + 1) as executor:
        for i in range(thread_num):
            executor.submit(run_browser_operation, result_queue, run_state, blog_url)
        #  启动计数线程
        executor.submit(count_success_count, result_queue, browser_count)

