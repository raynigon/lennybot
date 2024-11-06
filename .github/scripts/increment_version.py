import yaml

with open("version.txt", encoding="utf-8") as fp:
    version = fp.read()

parts = version.split(".")
parts[-1] = str(int(parts[-1]) + 1)
version = ".".join(parts)

with open("version.txt", "w", encoding="utf-8") as fp:
    fp.write(version)

with open("action.yml", encoding="utf-8") as fp:
    data = yaml.safe_load(fp)

data["runs"]["image"] = f"docker://ghcr.io/raynigon/lennybot:v{version}"

with open("action.yml", "w", encoding="utf-8") as fp:
    yaml.safe_dump(data, fp)
