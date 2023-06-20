[![PyPI](https://badge.fury.io/py/lennybot.svg)](https://pypi.org/project/lennybot/)
# lennybot

## Usage

### GitHub Actions
```
- uses: raynigon/lennybot@v1.0.0
  env:
    LB_CONFIG_FILE: ".github/lennybot.yaml"
    LB_GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}"
```

### CLI
Install package with `pip install lennybot`.
To start the application run the `lennybot` command.
You can specify the Action which should be executed.
This action can be "ci", "plan" or "apply".
The CI CLI action executed apply and handles git operations such as, commit and branch creation.
The plan action allows to plan updates and save the plan for later.
The apply action can either execute an existing plan, or create a new plan and apply it immediately.

### Docker
To run the lennybot as docker image execute:

```docker run --rm -v "$(pwd):/workspace/ raynigon/lennybot```

## How it works

The lennybot allows to define multiple applications.
Each application has to have a version source, which can be queried to determine the latest version.
If a newer version is available, the lennybot executes multiple pre defined actions per application.
E.g. Update Docker Image Tags.
The applications, sources and actions can be configured in the `config.yml` file.
For more information see below.

## Configuration
The lennybot can be configured via the `config.yml` file and environment variables.

If the `config.yml` file is not in the root of the current working directory, the `LB_CONFIG_FILE`environment variable can be used to pass the location of the configuration file to the lennybot.

The configuration file has multiple top level objects.
Each section represents a configuration object.

### State

| Path       | Description                                                           |
|------------|-----------------------------------------------------------------------|
| state.file | The state file which is used to store the version of each application |

### GitHub

| Path                                       | Description                                                            |
|--------------------------------------------|------------------------------------------------------------------------|
| state.file                                 | The state file which is used to store the version of each application  |
| state.pr.enabled                           | Toggle PR creation in CI mode. Has to be either true or false          |
| state.pr.repository                        | The name of the repository in github on which the PR should be created |
| state.pr.branchPrefix                      | Prefix for the branch name which should be used to create the PRs      |

### Applications

| Path                                       | Description                                                                                                                                |
|--------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| applications[*].name                       | The name of the application which should be updated                                                                                        |
| applications[*].source.type                | The source has to be either of the type "github" or of the type "github-query". See below for details. |
| applications[*].source.repository          | The GitHub Repository which should be used to determine the latest version                    |
| applications[*].source.regex               | The regex pattern which is used to extract the semver version code from the tag value         |
| applications[\*].actions[\*].type          | The action has to be one of these types "image-tag-update", "download-resources" or "update-yaml". See below for details. |
| applications[\*].actions[\*].url           |                                                                                                                                            |
| applications[\*].actions[\*].target        |                                                                                                                                            |
| applications[\*].actions[\*].image         |                                                                                                                                            |
| applications[\*].actions[\*].kustomizePath |                                                                                                                                            |
| applications[\*].actions[\*].tagPattern    |                                                                                                                                            |
| applications[\*].actions[\*].targetFile    |                                                                                                                                            |
| applications[\*].actions[\*].yamlPath      |                                                                                                                                            |
| applications[\*].actions[\*].valuePattern  |                                                                                                                                            |

#### GitHub Source
<TODO>

#### GitHub Query Source
<TODO>

#### Image Tag Update Action
<TODO>

#### Download Resource Action
<TODO>

#### Update YAML Action
<TODO>

#### Update Dockerfile Action
<TODO>

## Origin
Once upon time a colleague (Lenny) left my team.
Besides being an Apache Solr genius, one of the tasks he really liked doing, 
was the updating of the dependencies in our applications.
Since everyone else in the team didnt like this job, we needed some automation for this.
The lennybot was born to replace our colleague.
Since then the lennybot evolved and finally got replaced by the dependabot.
Some years later i needed a solution to upgrade components managed with kustomize.
This lead to the creation of a new lennybot which is able to automatically search for updates
and upgrades the resources with their latest versions.
