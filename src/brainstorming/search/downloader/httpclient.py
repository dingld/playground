import logging

import httpx
from httpx import Response

logger = logging.getLogger("fetcher.httpx")


def get(url: str, timeout: int = 15,
        proxy: str = "", cookies: list = None,
        headers: dict = None, trace_id: str = "") -> Response:
    if proxy:
        proxies = httpx.Proxy(proxy)
    else:
        proxies = None
    logger.info("httpx get url=%s, trace-id=%s", url, trace_id)
    return httpx.get(url, timeout=timeout, headers=headers, cookies=cookies, proxies=proxies)
