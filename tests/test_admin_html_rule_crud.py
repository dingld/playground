import logging
import unittest
from pprint import pformat

import requests

from scraperx.utils.config import set_config_level_fmt, read_config_key
from scraperx.utils.misc import get_project_path

logger = logging.getLogger("test.parser")


class AdminHtmlRuleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.url = "http://127.0.0.1:9090/api/v1/admin/rule"
        self.base_dir = get_project_path()
        self.rules = read_config_key("rules")
        set_config_level_fmt()


class AdminHtmlParserTest(AdminHtmlRuleTest):

    def test_load_all_rules_default(self):
        for rule in self.rules:
            self._create_rule(rule)

    def test_list_rules(self):
        for page in range(1, 4):
            resp = requests.get(self.url + "?page=%d" % page)
            for item in resp.json()['data']:
                logger.info(item)

    def test_create_rule_fail_missing(self):
        item = {
            "name": "baidu-search"
        }
        self._create_rule(item)

    def test_create_rule_success_or_duplicated(self):
        item = {
            "name": "baidu-search",
            "domain": "www.baidu.com",
            "path": "/s",
            "type": 10,
            "rules": [],
            "ttl": 60 * 60 * 24,
        }
        self._create_rule(item)

    def _create_rule(self, item: dict):
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
        self._update_rule(1, item)

    def _update_rule(self, rule_id: int, item: dict):
        resp = requests.put(self.url + "/%d" % rule_id, json=item)
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

    def test_put_rules_batch(self):
        rule_name_id_map = dict()
        for page in range(1, 4):
            resp = requests.get(self.url + "?page=%d" % page)
            for item in resp.json()['data']:
                rule_name_id_map[item['name']] = item['id']
        logger.info(rule_name_id_map)
        for rule in self.rules:
            if rule_name_id_map.get(rule['name']):
                logger.info("update rule: %s", rule)
                self._update_rule(rule_name_id_map.get(rule['name']), rule)
            else:
                logger.info("create rule: %s", rule)
                self._create_rule(rule)
