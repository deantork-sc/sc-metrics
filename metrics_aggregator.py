from github_api import GithubApi
from circleci_api import CircleciApi
from jira_api import JiraApi
import datetime

class MetricsAggregator:
    def __init__(self):
        self.github = GithubApi()
        self.circleci = CircleciApi()
        self.jira = JiraApi()

    def timediff_hours(self, start_datetime_obj, end_datetime_obj):
        delta = end_datetime_obj - start_datetime_obj
        # hours not stored in delta object - need to derive from days and seconds
        return delta.days * 24 + delta.seconds/3600

    def print_lead_time(self, project, limit):
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
    
    def print_change_fail(self, project, limit):
        # this query returns tickets created in the last 3 months that are tagged as bug/support in Silvercar with priority Highest/High
        jql_query = "(project = Silvercar) AND (type = Support OR type = Bug) AND \
            (priority = Highest OR priority = High) AND created > -90d order by createdDate DESC"
        builds_response = self.circleci.get_builds(project=project, limit=limit, filter="successful")
        builds = json.loads(builds_response.text)
        utcnow = datetime.datetime.utcnow()
        for build in builds:
            build_stop_datetime = self.circleci.format_time(build["stop_time"])
            build["age"] = self.timediff_hours(build_stop_datetime, utcnow)
        bugs_response = self.jira.search_issue(jql_query=jql_query)
        bugs = json.loads(builds_response.text)
        bugs_per_build = self.get_bugs_per_build(builds, bugs, utcnow)
        print()

    def get_bugs_per_build(self, builds, bugs, utcnow):
        """
            create an array (bugs_per_build) where each index = bugs that occurred during that build index
            i.e., build 0 is the first build (most recent successful one) we get back. 
            bugs_per_build[0] will be the number of bugs since the most recent build
            bugs_per_build[1] will be the number of bugs between build 1 (second most recent) and build 0
            etc.
        """
        # want to refactor to just get the number of builds we care about, then do bug_count / builds
        build_len = len(builds)
        bug_len = len(bugs)
        bugs_per_build = []
        build_index = 0
        bug_index = 0
        while (bug_index < bug_len) and (build_index < build_len):
            # for each bug:
            #   if bug age is less than current build, increment
            #   else, keep incrementing build_index until 
            bug_datetime = self.jira.format_time(bug["stop_time"])
            bug_age = self.timediff_hours(bug_datetime, utcnow)
            if bug_age < builds[build_index]["age"]:
                bugs_per_build[bug_index] += 1
                bug_index += 1
            else:
                build_index += 1
        return 


def main():
    metrics = MetricsAggregator()
    metrics.get_lead_time(project="dw-web", limit=10)

if __name__ == '__main__':
    main()
