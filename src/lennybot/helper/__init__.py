

def semver_2_vc(version):
    parts = version.split(".")
    version_code = 0
    for part in parts:
        version_code = version_code * 100 + int(part)
    return version_code