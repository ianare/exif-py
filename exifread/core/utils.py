"""
Misc utilities.
"""


def ord_(dta) -> int:
    if isinstance(dta, str):
        return ord(dta)
    return dta
