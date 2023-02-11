from parsel import Selector

from urllib3.util import parse_url, Url

_INDEX_CSS_RULES = {
    "www.google.com.hk": ".MjjYud",
    "www.baidu.com": ".c-container",
    "cn.bing.com": ".b_algo",
    "www.sogou.com": ".vrwrap",

}


def parse_index(text: bytes, url: str, default_css: str = "td[class]"):
    response = Selector(text=text, base_url=url)
    baseurl = response.css("base::attr(href)").extract_first() or url
    if not baseurl:
        msg = "parser_ml not supported baseurl missing: %s" % baseurl
        raise NotImplemented(msg)
    url_part: Url = parse_url(baseurl)
    css = _INDEX_CSS_RULES.get(url_part.netloc, default_css)

    for sel in response.css(css):
        sel: Selector = sel
        links, seen = [], set([])
        for link in sel.css("a::attr(href)").extract():
            if link in seen:
                continue
            seen.add(link)
            links.append(link)

        yield dict(
            text=sel.xpath("string(.)").extract_first(),
            links=links
        )


def parse_article(body: bytes, url: str, headers: dict = None, status_code: int = 200, default_css: str = ".content"):
    raise NotImplemented("parse article not implemented")


def parse_similar_single_page(body: bytes, url: str, headers: dict = None, status_code: int = 200,
                              default_css: str = ".content"):
    raise NotImplemented("parse article not implemented")
