import yaml
import sys

with open("version.txt") as fp:
    version = fp.read()

parts = version.split(".")
parts[-1] = str(int(parts[-1]) + 1)
version = ".".join(parts)

with open("version.txt", "w") as fp:
    fp.write(version)

with open("action.yml") as fp:
    data = yaml.safe_load(fp)

data["runs"]["image"] = f"docker://ghcr.io/raynigon/lennybot:v{version}"

with open("action.yml", "w") as fp:
    yaml.safe_dump(data, fp)
