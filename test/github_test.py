import unittest
import json
from unittest.mock import Mock, patch
from github_api import GithubApi


class TestGithubApi(unittest.TestCase):

    def setUp(self):
        self.github = GithubApi()

    def test_get_releases(self):
        response = self.github.get_releases("dw-web")
        self.assertEqual(response.status_code, 200)

    # @patch("github_api.requests.get")
    # def test_minor_releases(self, mock_get):
    #     # Start patching 'requests.get'.
    #     mock_get.return_value = Mock(status_code=470)
    #     response = self.github.get_releases("dw-web")
    #     self.assertEqual(response.status_code, 470)

    def test_older_than(self):
        newer = "2020-09-09T15:47:31Z"
        older = "2020-09-09T15:47:30Z"
        self.assertTrue(self.github.is_event_older_than_other(event=older, other=newer))

    def test_sort_prs(self):
        with open("test/test-data/test_prs.json") as prs_json:
            prs = json.load(prs_json)
        sorted_prs = self.github.sort_prs(prs)
        for i in range(1, len(sorted_prs)):
            time_diff = self.github.format_time(sorted_prs[i - 1]["merged_at"]) - self.github.format_time(sorted_prs[i]["merged_at"])
            self.assertTrue(time_diff.total_seconds() > 0)

    def test_get_feature_prs(self):
        with open("test/test-data/test_prs.json") as prs_json:
            prs = json.load(prs_json)
        feature_prs = list(filter(self.github.is_feature_pr, prs))
        self.assertEqual(len(feature_prs), 2)

    # def test_lead_time(self):
    #     with open("test/test-data/test_prs_with_starttime.json") as prs_json:
    #         prs = json.load(prs_json)
