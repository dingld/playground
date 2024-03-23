import logging
import os
import unittest
from pprint import pformat

import requests

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


class AdminHtmlRulePutTest(AdminHtmlScrapeTest):

    def setUp(self) -> None:
        super().setUp()
        self.rule_api = "http://127.0.0.1:9090/api/v1/admin/rule"
        self.rules_by_name = dict()
        self._get_html_rules()

    def _get_html_rules(self):
        for page in range(1, 4):
            resp = requests.get(self.rule_api + "?page=%d" % page)
            for item in resp.json()['data']:
                logger.info(item)
                self.rules_by_name[item['name']] = item

    def test_put_all_html(self):
        for name, rule in self.rules_by_name.items():
            url = "%s/%d/html" % (self.rule_api, rule['id'])
            logger.info("put rule html %s: %s", rule, url)
            rule['html'] = self.htmls[name + '.html']
            resp = requests.put(url, json=rule)
            logger.info(resp.json())

    def test_update_all_rules(self):
        for name, rule in self.rules_by_name.items():
            rule.update(self.rules.get(name, {}))
            url = "%s/%d" % (self.rule_api, rule['id'])
            logger.info("put rule %s: %s", rule['id'], url)
            resp = requests.put(url, json=rule)
            logger.info(resp.json())


class AdminHtmlScrapeSqlTest(AdminHtmlScrapeTest):

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


class AdminHtmlScrapeMLTest(AdminHtmlScrapeTest):

    def test_parse_baidu_search(self):
        html = self.htmls.get("douban-group-search.html")
        resp = requests.post(self.url + "/parse_ml", json=dict(url="https://www.baidu.com/s?",
                                                               html=html))
        items = resp.json()

        logger.info("cluster number: %d", len(items))
        javascript = """
        <script>
        function mOver(obj){
            selector = obj.getAttribute('targetCss')
           const myNodeList = document.querySelectorAll(selector);
            for (let i = 0; i < myNodeList.length; i++) {
            newObj = myNodeList[i]
            newObj.style.borderStyle='solid'
            newObj.style.borderColor='red'
            }
        }
        function mOut(obj){
             selector = obj.getAttribute('targetCss')
            const myNodeList = document.querySelectorAll(selector);
            for (let i = 0; i < myNodeList.length; i++) {
            newObj = myNodeList[i]
            newObj.style.borderStyle=null
            newObj.style.borderColor='red'
            }
        }
        </script>
        """

        style = """
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            border-bottom: 1px dotted black;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 120px;
            background-color: red;

        
            /* 定位 */
            position: absolute;
            z-index: 1;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
        }
        
                .sidebar {
          position: fixed;
          top: 50%;
          right: 0;
          transform: translateY(-50%);
          width: 200px;
          background-color: #f5f5f5;
          padding: 20px;
        }
        
        .sidebar ul {
          list-style: none;
          margin: 0;
          padding: 0;
        }
        
        .sidebar li {
          margin-bottom: 10px;
        }
        
        .sidebar a {
          text-decoration: none;
          color: #333;
        }
        
        </style>
        
        """

        divs = []
        for i, item in enumerate(items):
            rule = item.get('rule')
            logger.info("rule %d: %s", i, pformat(rule))
            css = rule['name']
            div = """
            <div onmouseover="mOver(this)" onmouseout="mOut(this)" class="tooltip mark-toggle" targetCss="%s"> %02d
                <span class="tooltiptext">%s</span>
            </div>
                """ % (css, i + 1, css)
            divs.append(div)
        div = """
        <div class="sidebar">marker
            %s
        </div>
        """ % "\n".join(divs)
        with open("baidu-search-template.html", "w+") as fp:
            fp.write(div + html + javascript + style)
