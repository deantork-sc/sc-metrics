# sc-metrics overview

## Goal metrics:
* Lead time: time from creating story to deployment in prod (CDT in CircleCI) (high dev prority)
* MTTR: time to restore from outage (high infrastructure priority)
* Deployment frequency: frequency of deployment to prod (med dev prority)
* Change fail percentage: how often major bugs are introduced (low dev prority)

## Sources:
* [JIRA](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
* [GitHub](https://docs.github.com/en/rest)
* CircleCI
* AWS (for MTTR)

### Misc.
Base it off of Accelerate Four Key Metrics
Want to group by scrum team and individual

# Working notes

## Lead time
#### Goal
Get the time it takes between creation of story and that story's deployment to the code
#### Ideas
If all tickets are closed as soon as they are merged into master, just get time discrepancy between when issue was opened and when it was closed
#### Programatic solution
* [Get all issues](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get) for a team in a given timespan
* Filter the issues to only see the closed issues
* Look at each [issue's changelog](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-changelog-get) to get time of creation and time that status was set to done
* Find the difference between the two 
* Find the average of these differences for a team/individual
#### Potential bugs
* Timezones

## MTTR
#### Goal
Get the time between all failing builds and the next successful build on the master branch
#### Ideas
Find all failing builds and then find the next successful build, find the time discrepancy between the two
#### Programatic solution
* Get [some number of builds](https://circleci.com/docs/api/#recent-builds-for-a-single-project) (30? 100?) for the project
* Filter these results to only be builds on master
* For each failing build, find the next successful build
* Find the difference between the two
* Find the average of these differences
#### Potential bugs
* Builds are for the whole project, how frequent are builds on master?

## Deployment frequency
#### Goal
Find the average time between successful deployments of a project
#### Ideas
Find all successful builds on master in CircleCI and get the average time discrepancy between them
#### Programatic solution
* Get [some number of builds](https://circleci.com/docs/api/#recent-builds-for-a-single-project) (30? 100?) for the project
* Filter these results to only be builds on master that succeeded
* Find the average difference between each build
#### Potential bugs
* Does successful build always == deployment?

## Change fail percentage
#### Goal
Find the percentage of master builds that fail
#### Ideas
For some number of builds on master, find what percentage failed compared to the percentage that succeeded
#### Programatic solution
* Get [some number of builds](https://circleci.com/docs/api/#recent-builds-for-a-single-project) (30? 100?) for the project
* Filter these results to only be builds on master that either succeeded or failed
* Calculate the ratio of failed builds to total
