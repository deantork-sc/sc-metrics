import unittest
from unittest.mock import Mock, patch
from github_api import GithubApi


class TestGithubApi(unittest.TestCase):

    def setUp(self):
        self.github = GithubApi()

    def test_get_releases(self):
        response = self.github.get_releases("dw-web")
        self.assertEqual(response.status_code, 200)

    @patch("github_api.requests.get")
    def test_minor_releases(self, mock_get):
        # Start patching 'requests.get'.
        mock_get.return_value = Mock(status_code=470)
        response = self.github.get_releases("dw-web")
        self.assertEqual(response.status_code, 470)
