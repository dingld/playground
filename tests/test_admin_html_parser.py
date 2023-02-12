import logging
import unittest
from pprint import pformat

import requests

from scraperx.utils.config import set_config_level_fmt

logger = logging.getLogger("test.parser")


class AdminTaskTest(unittest.TestCase):

    def setUp(self) -> None:
        self.url = "http://127.0.0.1:9090/api/v1/admin/html_parser"
        set_config_level_fmt()

    def test_create_task_fail_missing(self):
        item = {
            "name": "search"
        }
        self._create_task(item)

    def test_create_task_success_or_dupelicated(self):
        item = {
            "name": "search",
            "start_urls": ["https://www.baidu.com/s?wd=hello"],
            "cron": "30 8 * * *",
            "status": 0,
        }
        self._create_task(item)

    def _create_task(self, item: dict):
        resp = requests.post(self.url, json=item)
        logger.info("response status: %d", resp.status_code)
        logger.info(pformat(resp.json()))

    def test_get_task_by_id_success(self):
        for task_id in range(1, 4):
            resp = requests.get(self.url + "/%d" % task_id)
            logger.info("response status: %d", resp.status_code)
            logger.info(pformat(resp.json()))

    def test_update_task_success(self):
        item = {
            "name": "search-baidu",
            "start_urls": [
                "https://www.baidu.com/s?wd=hello",
            ],
            "cron": "30 8 * * *",
            "status": 0,
        }
        resp = requests.put(self.url + "/1", json=item)
        logger.info("response status: %d", resp.status_code)
        logger.info(pformat(resp.json()))

    def test_update_task_not_exist(self):
        item = {
            "name": "search",
            "start_urls": [
                "https://www.baidu.com/s?wd=hello",
                "https://cn.bing.com/search?q=hello"
            ],
            "cron": "30 8 * * *",
            "status": 0,
        }
        resp = requests.put(self.url + "/10086", json=item)
        logger.info("response status: %d", resp.status_code)
        logger.info(pformat(resp.json()))

    def test_list_tasks(self):
        for page in range(1, 4):
            resp = requests.get(self.url + "?page=%d" % page)
            logger.info(resp.json())

    def test_start_task_success(self):
        for task_id in [1, 10086]:
            resp = requests.post(self.url + "/{}/toggle/10".format(task_id))
            logger.info("response status: %d", resp.status_code)
            logger.info(pformat(resp.json()))

    def test_stop_task_success(self):
        for task_id in [1, 10086]:
            resp = requests.post(self.url + "/{}/toggle/0".format(task_id))
            logger.info("response status: %d", resp.status_code)
            logger.info(pformat(resp.json()))
