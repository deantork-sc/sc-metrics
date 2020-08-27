# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://silvercar.atlassian.net/rest/api/3/issue/HLP-3327/changelog"
with open('./config.json') as config:
    data = json.load(config)
    api_token = data["JIRA_API"]

auth = HTTPBasicAuth("dean.torkelson@silvercar.com", api_token)

headers = {
   "Accept": "application/json"
}

response = requests.request(
   "GET",
   url,
   headers=headers,
   auth=auth
)

print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))