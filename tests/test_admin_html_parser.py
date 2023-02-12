import logging
import unittest
from pprint import pformat

import requests

from scraperx.utils.config import set_config_level_fmt

logger = logging.getLogger("test.parser")


class AdminHtmlParserTest(unittest.TestCase):

    def setUp(self) -> None:
        self.url = "http://127.0.0.1:9090/api/v1/admin/html_parser"
        set_config_level_fmt()

    def test_create_rule_fail_missing(self):
        item = {
            "name": "baidu-search"
        }
        self._create_task(item)

    def test_create_rule_success_or_dupelicated(self):
        item = {
            "name": "baidu-search",
            "domain": "www.baidu.com",
            "path": "/s",
            "type": 10,
            "rules": [],
            "ttl": 60 * 60 * 24,
        }
        self._create_task(item)

    def _create_task(self, item: dict):
        resp = requests.post(self.url, json=item)
        logger.info("response status: %d", resp.status_code)
        logger.info(pformat(resp.json()))

    def test_get_rule_by_id_success(self):
        for task_id in range(1, 4):
            resp = requests.get(self.url + "/%d" % task_id)
            logger.info("response status: %d", resp.status_code)
            logger.info(pformat(resp.json()))

    def test_update_rule_success(self):
        item = {
            "name": "baidu-search",
            "domain": "www.baidu.com",
            "path": "/s",
            "type": 10,
            "rules": [
                "select * from response"
            ],
            "ttl": 60 * 60 * 24,
        }
        resp = requests.put(self.url + "/1", json=item)
        logger.info("response status: %d", resp.status_code)
        logger.info(pformat(resp.json()))

    def test_update_rule_not_exist(self):
        item = {
            "name": "baidu-search",
            "domain": "www.baidu.com",
            "path": "/s",
            "type": 10,
            "rules": [
                "select * from response"
            ],
            "ttl": 60 * 60 * 24,
        }
        resp = requests.put(self.url + "/10086", json=item)
        logger.info("response status: %d", resp.status_code)
        logger.info(pformat(resp.json()))

    def test_list_rules(self):
        for page in range(1, 4):
            resp = requests.get(self.url + "?page=%d" % page)
            logger.info(resp.json())

    def test_start_rule_success(self):
        for task_id in [1, 10086]:
            resp = requests.post(self.url + "/{}/toggle/10".format(task_id))
            logger.info("response status: %d", resp.status_code)
            logger.info(pformat(resp.json()))

    def test_stop_rule_success(self):
        for task_id in [1, 10086]:
            resp = requests.post(self.url + "/{}/toggle/20".format(task_id))
            logger.info("response status: %d", resp.status_code)
            logger.info(pformat(resp.json()))
