import logging

from httpx import AsyncClient

logger = logging.getLogger(__name__)

async def download_html(url: str, method: str = "GET") -> str:
    logger.info("downloading html %s", url)
    async with AsyncClient() as client:
        client.headers[
            'User-Agent'] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        resp = await client.request(method, url)
        await resp.aread()
        return resp.text
