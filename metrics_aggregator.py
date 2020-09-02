from github_api import GithubApi
from circleci_api import CircleciApi
from jira_api import JiraApi

class MetricsAggregator:
    def __init__(self):
        self.github = GithubApi()
        self.circleci = CircleciApi()
        self.jira = JiraApi()

    def get_lead_time(self, project, limit):
        delta_list = self.github.get_lead_time_array(project, limit)
        count = len(delta_list)
        if count == 0:
            print ("No PRs found with current criteria.")
            return
        delta_list.sort()
        average = round(sum(delta_list) / count, 2)
        median = round(delta_list[int(count / 2)], 2)
        print(f"Lead time metrics (in hours) for the last {count} feature PRs in {project}: ")
        print(f"  Median: {median}")
        print(f"  Average: {average}")

def main():
    metrics = MetricsAggregator()
    metrics.get_lead_time(project="dw-web", limit=10)

if __name__ == '__main__':
    main()
