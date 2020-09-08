jira:
	pipenv run python3 jira_api.py

circleci:
	pipenv run python3 circleci_api.py

github:
	pipenv run python3 github_api.py

metrics:
	pipenv run python3 metrics_aggregator.py

test: FORCE
	python3 -m unittest discover -s ./test -p '*_test.py'

FORCE:
