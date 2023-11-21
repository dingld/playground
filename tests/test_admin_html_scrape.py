import logging
import os
import unittest

import requests
from pprint import pformat

from scraperx.utils.config import read_config_key
from scraperx.utils.config import scan_files_in_dir
from scraperx.utils.config import set_config_level_fmt
from scraperx.utils.misc import get_project_path

logger = logging.getLogger("test.parser")


class AdminHtmlScrapeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.url = "http://127.0.0.1:9090/api/v1/admin/scrape"
        self.base_dir = get_project_path()
        self.rules = dict()
        for rule in read_config_key("rules"):
            self.rules.setdefault(rule['name'], rule)
        set_config_level_fmt()

        self.htmls = dict()
        self._init_with_html()

    def _init_with_html(self):
        for filepath in scan_files_in_dir(get_project_path(), suffix=".html"):
            basename = os.path.basename(filepath)
            with open(filepath) as fp:
                self.htmls.setdefault(basename, fp.read())

    def test_parse_baidu_search(self):
        resp = requests.post(self.url + "/parse", json=dict(url="https://www.baidu.com/s?",
                                                            html=self.htmls.get("baidu-search.html"),
                                                            rule=self.rules.get("baidu-search")))
        logger.info(pformat(resp.json()))

    def test_parse_bing_search(self):
        resp = requests.post(self.url + "/parse", json=dict(url="https://www.bing.com/search?",
                                                            html=self.htmls.get("bing-search.html"),
                                                            rule=self.rules.get("bing-search")))
        logger.info(pformat(resp.json()))

    def test_parse_google_search(self):
        resp = requests.post(self.url + "/parse", json=dict(url="https://www.google.com/search?",
                                                            html=self.htmls.get("google-search.html"),
                                                            rule=self.rules.get("google-search")))
        logger.info(pformat(resp.json()))