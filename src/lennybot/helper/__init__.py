

def semver_2_vc(version):
    parts = version.split(".")
    vc = 0
    for part in parts:
        vc = vc * 100 + int(part)
    return vc