from  core.utils import get_proxy_info
from core.browserOperation import BrowserOperationOnWebtraficRu
from core.utils import get_proxy_raw_by_api
from queue import Queue
from pathlib import Path
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
from core.model import ProxyRaw, Proxy
from core.utils import get_proxy_info


def handle_file(file_path: str) -> list[tuple[str, int]]:
    try:
        results = []
        with open(file_path, "r") as file:
            for line in file:
                items = line.strip().split(":")
                if items and len(items) == 2:
                    results.append((items[0], int(items[1])))
        return results
    except Exception as e:
        print(e)
        return []


def test_proxy(proxy_tuple: tuple[str, int]) -> Proxy | None:
    proxy_raw = ProxyRaw(ip=proxy_tuple[0], port=proxy_tuple[1])
    proxy_info = get_proxy_info(proxy_raw)
    if not proxy_info:
        print(f"代理信息获取失败：{proxy_tuple[0]}:{proxy_tuple[1]}")
        return None
    return proxy_info


def filter_proxy() -> list[Proxy] | None:
    proxies_sets: set[tuple[str, int]] = set()

    DIR = Path("proxyfile")

    with Pool(processes=6) as pool:
        txt_files_para = []
        # 获取一个路径下所有txt文件
        for txt_file in DIR.glob("*.txt"):
            txt_files_para.append(txt_file)

        async_results = pool.map_async(handle_file, txt_files_para)
        for process_result in async_results.get():
            for proxy in process_result:
                proxies_sets.add(proxy)
        print("代理数量：", len(proxies_sets))

    proxy_infos: list[Proxy] = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        results = executor.map(test_proxy, proxies_sets)
        for proxy_info in results:
            if proxy_info:
                print(proxy_info)
                proxy_infos.append(proxy_info)
    print('测试通过代理数量：', len(proxy_infos))
    with open("proxy_infos_filter.json", "w", encoding="utf-8") as f:
        for proxy_info in proxy_infos:
            f.write(proxy_info.model_dump_json() + "\n")

    return proxy_infos


def run_browser_operation(_result_queue: Queue, _run_state: dict[str, bool], _blog_url: str, proxy_info: Proxy):
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


def count_success_count(_result_queue: Queue, _run_state: dict[str, bool]):
    success_count = 0
    while True:
        if not _run_state["state"]:
            print("\n任务完成！")
            break
        result = _result_queue.get()
        if result:
            success_count += 1
            print(f"\r成功次数：{success_count}", end="")


if __name__ == '__main__':
    # 获取本地文件代理
    proxy_infos: list[Proxy] = filter_proxy()
    run_state: dict[str, bool] = {"state": True}
    result_queue: Queue[bool] = Queue()
    blog_url = "https://ssson966.blogspot.com/2025/09/linuxerror-while-loading-shared.html"

    with ThreadPoolExecutor(max_workers=21) as executor:
        results = []
        for proxy_info_ in proxy_infos:
            results.append(executor.submit(run_browser_operation, result_queue, run_state, blog_url, proxy_info_))
         # 启动计数线程
        # executor.submit(count_success_count, result_queue, run_state)
        results_end = [result.result() for result in results]
        print(f"运行结束，成功次数：{results_end.count(True)}")
