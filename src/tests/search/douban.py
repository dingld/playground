from unittest import TestCase

from brainstorming.search.downloader import httpclient

from brainstorming.search.site.douban import sign_frodo_url, FRODO_USER_AGENT


class TestFrodoApi(TestCase):

    def test_group_topic(self):
        url = "https://frodo.douban.com/api/v2/group/szsh/topics"
        signed_url = sign_frodo_url("GET", url)
        print(signed_url)
        response = httpclient.get(signed_url, headers={"User-Agent": FRODO_USER_AGENT})
        print(response.json())
