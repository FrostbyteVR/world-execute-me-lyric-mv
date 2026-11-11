"""A plain, correct shot for any shot id that has no drawing in wem/sections yet."""
from .kit import section_fallback


def fallback_spec(env, row):
    return section_fallback(env, row)
