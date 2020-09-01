import requests
from requests.auth import HTTPBasicAuth
import json

class GithubApi:
    def __init__(self):
        with open('./config.json') as config:
            data = json.load(config)
            token = data["GITHUB_PAT"]
        self.headers = { 
            "Accept": "application/json",
            "Authorization": f"token {token}" }

    def get_commits(self):
        url = f"https://api.github.com/repos/silvercar/dw-vin-decoder/commits"
        return requests.request( "GET", url, headers=self.headers)


github = GithubApi()
response = github.get_commits()
print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))