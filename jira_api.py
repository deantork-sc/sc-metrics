# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

class JiraApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            api_token = data["JIRA_API"]
        self.auth = HTTPBasicAuth("dean.torkelson@silvercar.com", api_token)
        self.headers = { "Accept": "application/json" }

    def get_issue_changelog(self, issue_id):
        url = f"https://silvercar.atlassian.net/rest/api/3/issue/{issue_id}/changelog"
        return requests.request( "GET", url, headers=self.headers, auth=self.auth)

    def get_single_issue_leadtime(self, issue_id):
        response = self.get_issue_changelog(issue_id)
        response_json = json.loads(response.text)
        print(json.dumps(response_json, sort_keys=True, indent=4, separators=(",", ": ")))


jira = JiraApi()
jira.get_single_issue_leadtime("HLP-3327")