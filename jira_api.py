import requests
from requests.auth import HTTPBasicAuth
import json
import datetime


class JiraApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            api_token = data["JIRA_API"]
        self.auth = HTTPBasicAuth("dean.torkelson@silvercar.com", api_token)
        self.headers = {"Accept": "application/json"}

    def format_time(self, datetime_str):
        format_string = "%Y-%m-%dT%H:%M:%S.%f%z"
        return datetime.datetime.strptime(datetime_str, format_string)

    def get_issue_changelog(self, issue_id):
        url = f"https://silvercar.atlassian.net/rest/api/3/issue/{issue_id}/changelog"
        return requests.request("GET", url, headers=self.headers, auth=self.auth)

    def get_group(self):
        url = f"https://silvercar.atlassian.net/rest/api/3/groupuserpicker?query=dean"
        return requests.request("GET", url, headers=self.headers, auth=self.auth)

    def search_issue(self, jql_query):
        url = f"https://silvercar.atlassian.net/rest/api/3/search?jql={jql_query}"
        return requests.request("GET", url, headers=self.headers, auth=self.auth)

    def get_issue(self):
        url = f"https://silvercar.atlassian.net/rest/api/3/issue/HLP-3335"
        return requests.request("GET", url, headers=self.headers, auth=self.auth)

    def demo(self):
        changelog = self.get_issue_changelog("HLP-3335").text
        with open('changelog.json', 'w') as outfile:
            json.dump(json.loads(changelog), outfile)

        group = self.get_group().text
        with open('group.json', 'w') as outfile:
            json.dump(json.loads(group), outfile)

        jql_query = "(project = Silvercar) AND (type = Support OR type = Bug) AND " + \
                    f"(priority = Highest OR priority = High) AND created > -182d order by createdDate DESC"
        search = self.search_issue(jql_query).text
        with open('search.json', 'w') as outfile:
            json.dump(json.loads(search), outfile)

        issue = self.get_issue().text
        with open('issue.json', 'w') as outfile:
            json.dump(json.loads(issue), outfile)
