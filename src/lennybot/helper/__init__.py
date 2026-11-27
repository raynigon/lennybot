from typing import Tuple


def semver_2_vc(version) -> Tuple[int, ...]:
    """
    Converts a dotted version (e.g. "2.4.311331") into a comparable version code.
    Each component is compared numerically, so components with any number of digits sort correctly.
    """
    if version is None:
        return ()
    return tuple(int(part) for part in version.split("."))
