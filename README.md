# lennybot

## Origin
One upon time a colleague (Lenny) left my team.
One of the tasks he really liked doing, was the updating of the dependencies in our applications.
Since everyone else in the team didnt like this job, we needed some automation for this.
The lennybot was born to replace our colleague.
Since then the lennybot evolved and finally got replaced by the dependabot.
Some years later i needed a solution to upgrade components managed with kustomize.
This lead to the creation of a new lennybot which is able to automatically search for updates
and upgrades the resources with their latest versions.

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

### Docker
To run the lennybot as docker image execute:

```docker run --rm -v "$(pwd):/workspace/ raynigon/lennybot```

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

| Path       | Description                                                           |
|------------|-----------------------------------------------------------------------|
| state.file | The state file which is used to store the version of each application |

### Applications

| Path                                       | Description                                                                                                                                |
|--------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| applications[*].name                       | The name of the application which should be updated                                                                                        |
| applications[*].source.type                | The type of source which should be used to determine the latest version for the application. (has to be one of "github" or "github-query") |
| applications[*].source.repository          | The GitHub Repository which should be used to determine the latest version                                                                 |
| applications[*].source.regex               | The regex pattern which is used to extract the semver version code from the tag value                                                      |
| applications[\*].actions[\*].type          |                                                                                                                                            |
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
