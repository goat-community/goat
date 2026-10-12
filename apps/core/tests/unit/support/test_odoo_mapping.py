from datetime import UTC, datetime

import pytest
from core.support import odoo_mapping as m

pytestmark = pytest.mark.unit


def test_stage_mapping_round_trips() -> None:
    for name, status in m.STATUS_BY_STAGE_NAME.items():
        assert m.STAGE_NAME_BY_STATUS[status] == name
    assert m.STATUS_BY_STAGE_NAME["Waiting on Customer"] == "waiting"


def test_category_from_tags() -> None:
    assert m.category_from_tag_names(["web-ui", "data-question"]) == "data_issue"
    assert m.category_from_tag_names(["web-ui"]) == "other"
    assert m.category_from_tag_names([]) == "other"
    assert m.TAG_BY_CATEGORY["other"] is None


def test_impact_priority_mapping() -> None:
    assert m.PRIORITY_BY_IMPACT == {"blocking": "2", "slowing": "1", "question": "0"}
    assert (
        m.impact_from_priority("3") == "blocking"
    )  # agent-set Urgent reads as blocking
    assert m.impact_from_priority("0") == "question"
    assert m.impact_from_priority(None) is None


def test_customer_facing_messages() -> None:
    public_ids = frozenset({1})
    assert m.is_customer_facing(
        {
            "message_type": "comment",
            "is_internal": False,
            "subtype_id": [1, "Discussions"],
        },
        public_ids,
    )
    assert m.is_customer_facing(
        {
            "message_type": "email",
            "is_internal": False,
            "subtype_id": [1, "Discussions"],
        },
        public_ids,
    )
    assert not m.is_customer_facing(
        {
            "message_type": "comment",
            "is_internal": True,
            "subtype_id": [1, "Discussions"],
        },
        public_ids,
    )
    assert not m.is_customer_facing(
        {
            "message_type": "notification",
            "is_internal": False,
            "subtype_id": [1, "Discussions"],
        },
        public_ids,
    )
    assert not m.is_customer_facing(
        {
            "message_type": "auto_comment",
            "is_internal": False,
            "subtype_id": [1, "Discussions"],
        },
        public_ids,
    )
    # Internal subtype (Note, not in the public set) even with is_internal=False
    assert not m.is_customer_facing(
        {"message_type": "comment", "is_internal": False, "subtype_id": [2, "Note"]},
        public_ids,
    )
    # No subtype_id set
    assert not m.is_customer_facing(
        {"message_type": "comment", "is_internal": False, "subtype_id": False},
        public_ids,
    )
    assert not m.is_customer_facing(
        {"message_type": "comment", "is_internal": False}, public_ids
    )
    # Unknown subtype id: allow-list, so not shown
    assert not m.is_customer_facing(
        {"message_type": "comment", "is_internal": False, "subtype_id": [99, "X"]},
        public_ids,
    )
    # Nothing known as public: nothing is shown
    assert not m.is_customer_facing(
        {
            "message_type": "comment",
            "is_internal": False,
            "subtype_id": [1, "Discussions"],
        },
        frozenset(),
    )


def test_strips_images_carrying_odoo_urls() -> None:
    body = (
        '<p>Hi<img src="/web/image/2962?access_token=abc" width="272"></p>'
        '<img src="https://odoo.example.org/web/content/5?access_token=x">'
        '<img src="https://example.org/logo.png"><p>end</p>'
    )
    assert m.strip_odoo_images(body) == (
        '<p>Hi</p><img src="https://example.org/logo.png"><p>end</p>'
    )


def test_parse_datetime() -> None:
    assert m.parse_datetime("2026-09-30 14:07:05") == datetime(
        2026, 9, 30, 14, 7, 5, tzinfo=UTC
    )
    assert m.parse_datetime(False) is None


def test_many2one_helpers() -> None:
    assert m.many2one_id([7, "Lena"]) == 7
    assert m.many2one_name([7, "Lena"]) == "Lena"
    assert m.many2one_id(False) is None
    assert m.many2one_name(False) is None


def test_file_names_lose_direction_controls() -> None:
    assert m.file_name("invoice\u202efdp.exe") == "invoicefdp.exe"
    assert m.file_name("a\u2066b\u2069\u200fc.pdf") == "abc.pdf"
    assert m.file_name("\u202e") == "file"
    assert m.file_name(False) == "file"
    assert m.file_name("Karte_ÄÖÜ.png") == "Karte_ÄÖÜ.png"
