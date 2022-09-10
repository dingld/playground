import asyncio
import logging
import time
import traceback

from asgiref.sync import async_to_sync
from pyppeteer.browser import Browser, Page
from pyppeteer.launcher import connect
from w3lib.url import urlparse

from entity.request import CrawlerRequest
from entity.response import CrawlerResponse
from lib.cookie import format_cookies
from lib.main.worker import app

logger = logging.getLogger("fecher.chrome")


@app.task(name="fetcher.chrome")
def fetch_url(url: str, timeout: int = 15, wait_for: float = 0.5, proxy: str = "",
              cookies: list = None, headers: dict = None, task: str = "") -> str:
    request = CrawlerRequest.new(url=url, task=task, timeout=timeout, proxy=proxy,
                                 cookies=cookies, headers=headers, wait_for=wait_for)
    response = chrome_fetch_sync(request, app.conf.get("browser_url"))
    return response.text


def chrome_fetch_sync(request: CrawlerRequest, browser_url: str) -> CrawlerResponse:
    response = async_to_sync(fetch)(request=request, browser_url=browser_url)
    if response.status_code != 200:
        raise Exception("http_code=%s, url=%s" % (response.status_code, response.url))
    return response


async def fetch(request: CrawlerRequest, browser_url) -> CrawlerResponse:
    """
    fetch url as browser
    :return:
    """
    t0 = time.time()
    proxy = request.proxy

    if "?" in browser_url:
        browser_url = browser_url + "&"
    else:
        browser_url = browser_url + "?"
    browser_url = "%s--disable-features=UserAgentClientHint" % (browser_url)

    if proxy:
        browser_url = "%s&--proxy-server=%s" % (browser_url, proxy)
    page, browser, t = await _create_page(browser_url)

    asyncio.get_event_loop().create_task(_close_browser(browser, request.timeout, request.url))
    await _init_cookies(request, page)
    response = await page.goto(request.url, timeout=request.timeout * 1000)
    await page.waitFor(request.wait_for or 0.5)
    content = await page.content()
    headers = response.headers
    headers['Set-Cookie'] = format_cookies(await page.cookies(response.url))
    t.cancel()
    asyncio.get_event_loop().create_task(_close_browser(browser, 0, request.url))
    crawler_response = CrawlerResponse.construct(url=request.url, task=request.task,
                                                 status_code=response.status,
                                                 headers=headers, text=content,
                                                 download_delay=time.time() - t0)
    return crawler_response


async def _init_cookies(request: CrawlerRequest, page: Page):
    if request.headers:
        await page.setExtraHTTPHeaders(request.headers)
    domain = urlparse(request.url).netloc
    cookies = app.conf.get("default_cookies", [])
    for cookie in cookies:
        cookie.setdefault("domain", domain)
        try:
            logger.debug("set cookie: %s", cookie)
            await page.setCookie(cookie)
        except Exception as e:
            logger.error("set cookie %s: %s", e, cookie)


def _format_chrome_cookie(cookie: str):
    pair = cookie.split("=", maxsplit=1)
    return {"name": pair[0].strip(), "value": pair[1].strip(), "path": "/"}


async def _create_page(uri: str, seconds: int = 15):
    logger.info("chrome opening uri=%s", uri)
    browser = await connect(browserWSEndpoint=uri)
    t = asyncio.get_event_loop().create_task(_close_browser(browser, seconds, uri))
    return await browser.newPage(), browser, t


async def _close_browser(browser: Browser, seconds: float, uri: str):
    await asyncio.sleep(seconds)
    try:
        await browser.close()
        logger.debug("chrome closed uri=%s", uri)
    except ConnectionError as e:
        logger.debug("connection err %s", e)
    except Exception as e:
        logger.error("chrome unclosed err=%s", e)
        logger.error(traceback.format_exc())
