import yaml
import sys

with open("action.yml") as fp:
    data = yaml.safe_load(fp)

version = sys.argv[1]
data["runs"]["image"] = f"docker://ghcr.io/raynigon/lennybot:{version}"

with open("action.yml", "w") as fp:
    yaml.safe_dump(data, fp)
