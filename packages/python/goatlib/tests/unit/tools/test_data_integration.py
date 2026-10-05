"""Tag filters compiled to SQL.

The part with logic in it: a tag condition becomes two tests, and both have to
agree. `LIKE '%amenity%'` would match `amenity:parking`, and a value typed by a
user reaches a string literal.
"""

import pytest
from goatlib.tools import data_integration as module
from goatlib.tools.data_integration import FEATURE_TYPES, TagFilter, _tag_sql


def test_a_key_and_value_match_the_whole_pair() -> None:
    pre, exact = _tag_sql([TagFilter(key="amenity", value="restaurant")])
    # The quotes are what stop `amenity` matching `amenity:parking`.
    assert pre == 'regexp_matches(all_tags, \'"amenity"=>"restaurant"\')'
    assert exact == "tags['amenity'] = 'restaurant'"


def test_a_key_alone_matches_any_value() -> None:
    pre, exact = _tag_sql([TagFilter(key="amenity")])
    assert pre.endswith("'\"amenity\"=>')")
    assert exact == "map_contains(tags, 'amenity')"


def test_no_filter_keeps_everything_in_the_area() -> None:
    assert _tag_sql([]) == ("TRUE", "TRUE")


@pytest.mark.parametrize("value", ["O'Brien", "a'); DROP TABLE t; --"])
def test_a_quote_cannot_end_the_literal(value) -> None:
    _, exact = _tag_sql([TagFilter(key="name", value=value)])
    # Doubled, so it stays inside its own quotes.
    assert "''" in exact and exact.count("'") % 2 == 0


def test_every_feature_type_names_a_geometry() -> None:
    assert set(FEATURE_TYPES) == {"points", "lines", "multipolygons"}


def test_the_cache_key_changes_with_the_snapshot(tmp_path, monkeypatch) -> None:
    """Building the tag list costs ten seconds, so it is kept. Keeping it across
    a new weekly mirror would answer this week's question from last week's data."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    env = (11.5, 48.1, 11.6, 48.2)
    last = module._tag_cache_path("layer-1", "points", [("germany", "20260921")], env)
    this = module._tag_cache_path("layer-1", "points", [("germany", "20260928")], env)
    assert last != this
    # And a different area, or a different geometry, is a different question.
    assert last != module._tag_cache_path("layer-2", "points", [("germany", "20260921")], env)
    assert last != module._tag_cache_path("layer-1", "lines", [("germany", "20260921")], env)
