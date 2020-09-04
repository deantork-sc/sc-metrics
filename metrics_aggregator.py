from github_api import GithubApi
from circleci_api import CircleciApi
from jira_api import JiraApi
import datetime
import json

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
    
    def print_change_fail(self):
        # this query returns tickets created in the last year that are tagged as bug/support
        # in Silvercar with priority Highest/High
        jql_query = "(project = Silvercar) AND (type = Support OR type = Bug) AND \
            (priority = Highest OR priority = High) AND created > -52w order by createdDate DESC"
        # assuming that we're just going
        releases_response = self.github.get_releases(project="dw-web")
        releases = json.loads(releases_response.text)
        utcnow = datetime.datetime.utcnow()
        release_count = 0
        for release in releases:
            release_count += 1
            time_since_release = self.github.format_time(release["published_time"]) - datetime.datetime.utcnow()
            if (time_since_release.days > 365):
                releases = releases[:release_count+1]
        with open('releases_year.json', 'w') as outfile:
            json.dump(releases, outfile)
        bugs_response = self.jira.search_issue(jql_query=jql_query)
        bugs_count = len(json.loads(bugs_response.text))
        print(f"Got {len(releases)} releases and {bugs_count} bugs.")

    def get_bugs_per_build(self, deployments, bugs, utcnow):
        """
            create an array (bugs_per_build) where each index = bugs that occurred during that build index
            i.e., build 0 is the first build (most recent successful one) we get back. 
            bugs_per_build[0] will be the number of bugs since the most recent build
            bugs_per_build[1] will be the number of bugs between build 1 (second most recent) and build 0
            etc.
        """
        # want to refactor to just get the number of builds we care about, then do bug_count / builds
        deployment_count = len(deployments)
        bug_count = len(bugs)
        bugs_per_build = []
        build_index = 0
        bug_index = 0
        while (bug_index < bug_count) and (build_index < deployment_count):
            # for each bug:
            #   if bug age is less than current build, increment
            #   else, keep incrementing build_index until 
            bug_datetime = self.jira.format_time(bugs[bug_index]["stop_time"])
            bug_age = self.timediff_hours(bug_datetime, utcnow)
            if bug_age < deployments[build_index]["age"]:
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
