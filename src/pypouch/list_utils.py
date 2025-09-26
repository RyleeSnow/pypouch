def list_inter(a: list, b: list) -> list:
    """Return the intersection of two lists"""

    return list(set(a).intersection(set(b)))


def list_diff(a: list, b: list) -> list:
    """Return the difference of two lists"""

    return list(set(a).difference(set(b)))


def list_sym_diff(a: list, b: list) -> list:
    """Return the symmetric difference of two lists, in a or in b but not in both"""
    return list(set(a) ^ set(b))


def list_union(a: list, b: list) -> list:
    """Return the union of two lists"""
    return list(set(a).union(set(b)))