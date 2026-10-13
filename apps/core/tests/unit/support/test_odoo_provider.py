import base64
from typing import Any

import pytest
from core.support.errors import SupportUnavailable
from core.support.odoo_client import OdooRejected
from core.support.odoo_provider import OdooSupportProvider
from core.support.types import NewTicket, TicketQuery, UploadedFile

from .fakes import STAGES, TAGS, action_ops, base_odoo, op_calls, ticket_record

pytestmark = pytest.mark.unit

DISCUSSION = [1, "Discussions"]
NOTE = [2, "Note"]


def _provider(odoo: Any) -> OdooSupportProvider:
    return OdooSupportProvider(
        odoo, team_id=1, post_action_name="GOAT: post message as ticket participant"
    )


async def test_find_contact_asks_the_server_action_with_normalized_emails() -> None:
    odoo = base_odoo(contacts={"first_last@stadt.de": 7})
    found = await _provider(odoo).find_contacts_by_email(["  First_Last@Stadt.DE "])
    assert found == {"first_last@stadt.de": 7}
    (ask,) = op_calls(odoo, "find")
    assert ask["goat_emails"] == ["first_last@stadt.de"]
    assert ask["goat_prefer_company_id"] == 0
    found = await _provider(odoo).find_contacts_by_email(
        ["a@x.de"], prefer_company_id=500
    )
    assert found == {}
    assert op_calls(odoo, "find")[1]["goat_prefer_company_id"] == 500
    # contacts are never read directly: the bridge reads only GOAT contacts
    assert not [c for c in odoo.calls if c[0] == "res.partner"]


async def test_find_contact_sends_at_most_fifty_emails_at_once() -> None:
    odoo = base_odoo(contacts={"a7@x.de": 7, "a77@x.de": 77})
    emails = [f"a{n}@x.de" for n in range(120)]
    found = await _provider(odoo).find_contacts_by_email(emails)
    assert found == {"a7@x.de": 7, "a77@x.de": 77}
    asks = [a["goat_emails"] for a in op_calls(odoo, "find")]
    assert [len(a) for a in asks] == [50, 50, 20]
    assert sorted(e for a in asks for e in a) == sorted(emails)
    assert await _provider(odoo).find_contacts_by_email([" ", ""]) == {}
    assert len(op_calls(odoo, "find")) == 3


async def test_create_contact_goes_through_the_server_action() -> None:
    odoo = base_odoo().on(
        "ir.actions.server",
        "run",
        lambda kw: {"type": "ir.actions.act_window_close", "goat_contact_id": 42},
    )
    cid = await _provider(odoo).create_contact(
        name="Anna Keller", email="anna@x.de", lang="de", company_id=500
    )
    assert cid == 42
    assert odoo.calls_to("res.partner", "create") == []
    (run,) = odoo.calls_to("ir.actions.server", "run")
    assert run["ids"] == [1562]
    assert run["context"] == {
        "goat_op": "contact",
        "goat_name": "Anna Keller",
        "goat_email": "anna@x.de",
        "goat_lang": "de_DE",
        "goat_parent_id": 500,
    }
    await _provider(odoo).create_contact(
        name="B", email="b@x.de", lang="en", company_id=None
    )
    assert (
        odoo.calls_to("ir.actions.server", "run")[1]["context"]["goat_parent_id"] == 0
    )


async def test_the_bridges_own_partner_is_looked_up_once() -> None:
    provider = _provider(odoo := base_odoo())
    assert await provider.bridge_contact_id() == 43402
    assert await provider.bridge_contact_id() == 43402
    assert len(odoo.calls_to("res.users", "context_get")) == 1
    assert odoo.calls_to("res.users", "read") == [
        {"ids": [16], "fields": ["partner_id"]}
    ]


async def test_list_builds_an_or_domain_including_followed_tickets() -> None:
    odoo = (
        base_odoo(
            people={
                300: {"name": "Lena", "staff": True},
                100: {"name": "Marco", "staff": False},
            }
        )
        .on_op("followed", lambda ctx: {"goat_ticket_ids": [29]})
        .on("helpdesk.ticket", "search_read", lambda kw: [ticket_record()])
        .on(
            "mail.message",
            "search_read",
            lambda kw: [
                {
                    "id": 71,
                    "res_id": 31,
                    "author_id": [300, "Lena"],
                    "date": "2026-09-30 11:05:00",
                    "message_type": "comment",
                    "is_internal": False,
                    "subtype_id": NOTE,
                },
                {
                    "id": 70,
                    "res_id": 31,
                    "author_id": [300, "Lena"],
                    "date": "2026-09-30 11:02:00",
                    "message_type": "comment",
                    "is_internal": False,
                    "subtype_id": DISCUSSION,
                },
                {
                    "id": 69,
                    "res_id": 31,
                    "author_id": [100, "Marco"],
                    "date": "2026-09-29 09:00:00",
                    "message_type": "comment",
                    "is_internal": False,
                    "subtype_id": DISCUSSION,
                },
            ],
        )
    )
    tickets = await _provider(odoo).list_tickets(
        TicketQuery(
            customer_ids=(100,), follower_contact_id=100, org_id="org-1", open=True
        )
    )
    (domain_call,) = odoo.calls_to("helpdesk.ticket", "search_read")
    domain = domain_call["domain"]
    assert domain[:2] == [["team_id", "=", 1], ["stage_id", "in", [1, 2, 3]]]
    assert domain[2:] == [
        "|",
        "|",
        ["partner_id", "in", [100]],
        ["id", "in", [29]],
        ["x_goat_organization_id", "=", "org-1"],
    ]
    (message_call,) = odoo.calls_to("mail.message", "search_read")
    assert "subtype_id" in message_call["fields"]
    (t,) = tickets
    assert (t.ref, t.status, t.category, t.impact) == (
        "00031",
        "in_progress",
        "bug",
        "blocking",
    )
    # message 71 is a log note (internal subtype) and must not count as the latest message
    assert (
        t.latest_message_id,
        t.latest_message_author,
        t.latest_message_is_agent,
    ) == (70, "Lena", True)
    assert t.via == "app"


async def test_list_with_nothing_to_match_does_not_query() -> None:
    odoo = base_odoo()
    assert await _provider(odoo).list_tickets(TicketQuery((), None, None, None)) == []
    assert odoo.calls_to("helpdesk.ticket", "search_read") == []


async def test_stage_names_are_read_in_english() -> None:
    odoo = base_odoo().on("helpdesk.ticket", "write", lambda kw: True)
    await _provider(odoo).set_status(31, "waiting")
    (stage_call,) = odoo.calls_to("helpdesk.stage", "search_read")
    assert stage_call["context"] == {"lang": "en_US"}
    assert odoo.calls_to("helpdesk.ticket", "write") == [
        {"ids": [31], "vals": {"stage_id": 3}}
    ]


DETAIL_PEOPLE = {
    100: ("Marco", False),
    300: ("Lena", True),
    2: ("OdooBot", True),
    26: ("Majk", True),
    101: ("Anna", False),
}


def _detail_people(photos: dict[int, Any] | None = None) -> dict[int, dict[str, Any]]:
    """What the "people" op knows about _detail_odoo's partners; `photos` by id."""
    return {
        i: {"name": n, "staff": s, "photo": (photos or {}).get(i)}
        for i, (n, s) in DETAIL_PEOPLE.items()
    }


def _detail_odoo(
    extra_messages: list[dict[str, Any]] | None = None,
    photos: dict[int, Any] | None = None,
) -> Any:
    messages = [
        {
            "id": 60,
            "author_id": [100, "Marco"],
            "date": "2026-09-28 09:14:00",
            "body": "<p>Hi</p>",
            "message_type": "comment",
            "is_internal": False,
            "subtype_id": DISCUSSION,
            "attachment_ids": [900],
        },
        {
            "id": 61,
            "author_id": [2, "OdooBot"],
            "date": "2026-09-28 09:14:01",
            "body": "<p>Ticket received</p>",
            "message_type": "auto_comment",
            "is_internal": False,
            "subtype_id": NOTE,
            "attachment_ids": [],
        },
        {
            "id": 62,
            "author_id": [300, "Lena"],
            "date": "2026-09-28 11:02:00",
            "body": '<p>Fix soon<img src="/web/image/5?access_token=t"></p>',
            "message_type": "email",
            "is_internal": False,
            "subtype_id": DISCUSSION,
            "attachment_ids": [],
        },
        *(extra_messages or []),
    ]
    return (
        base_odoo(people=_detail_people(photos))
        .on("helpdesk.ticket", "search_read", lambda kw: [ticket_record()])
        .on("mail.message", "search_read", lambda kw: messages)
        .on(
            "ir.attachment",
            "read",
            lambda kw: [
                {"id": a, "name": "map.png", "mimetype": "image/png", "file_size": 1234}
                for a in kw["ids"]
            ],
        )
        .on_op("followers", lambda ctx: {"goat_partner_ids": [100, 26, 101]})
    )


async def test_get_ticket_maps_thread_and_followers() -> None:
    odoo = _detail_odoo()
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert [m.id for m in detail.messages] == [60, 62]  # auto mail left out
    assert detail.messages[1].is_agent and detail.messages[1].via == "email"
    assert "<img" not in detail.messages[1].body_html
    assert detail.messages[0].attachments[0].name == "map.png"
    assert {(f.contact_id, f.is_internal) for f in detail.followers} == {
        (100, False),
        (26, True),
        (101, False),
    }
    (message_call,) = odoo.calls_to("mail.message", "search_read")
    assert "subtype_id" in message_call["fields"]


async def test_log_note_is_not_shown() -> None:
    # Odoo stores log notes as comment / is_internal=False with the internal "Note" subtype.
    note = {
        "id": 63,
        "author_id": [300, "Lena"],
        "date": "2026-09-28 12:00:00",
        "body": "<p>internal</p>",
        "message_type": "comment",
        "is_internal": False,
        "subtype_id": NOTE,
        "attachment_ids": [902],
    }
    odoo = _detail_odoo([note])
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert [m.id for m in detail.messages] == [60, 62]
    assert 902 not in detail.visible_attachment_ids
    assert detail.visible_attachment_ids == frozenset({900})
    (subtype_call,) = odoo.calls_to("mail.message.subtype", "search_read")
    assert subtype_call["domain"] == [["internal", "=", False]]


async def test_public_subtypes_are_looked_up_once() -> None:
    odoo = _detail_odoo()
    provider = _provider(odoo)
    await provider.get_ticket("00031")
    await provider.get_ticket("00031")
    assert len(odoo.calls_to("mail.message.subtype", "search_read")) == 1


async def test_empty_subtype_lookup_is_not_cached() -> None:
    # An empty allow-list would hide every message; it must be retried, not remembered.
    answers: list[list[dict[str, Any]]] = [[], [{"id": 1}]]
    odoo = _detail_odoo().on(
        "mail.message.subtype", "search_read", lambda kw: answers.pop(0)
    )
    provider = _provider(odoo)
    first = await provider.get_ticket("00031")
    assert first is not None and first.messages == ()
    second = await provider.get_ticket("00031")
    assert second is not None and [m.id for m in second.messages] == [60, 62]
    assert len(odoo.calls_to("mail.message.subtype", "search_read")) == 2


async def test_empty_stage_and_tag_lookups_are_not_cached() -> None:
    stage_answers: list[list[dict[str, Any]]] = [[], STAGES]
    tag_answers: list[list[dict[str, Any]]] = [[], TAGS]
    odoo = (
        _detail_odoo()
        .on("helpdesk.stage", "search_read", lambda kw: stage_answers.pop(0))
        .on("helpdesk.tag", "search_read", lambda kw: tag_answers.pop(0))
    )
    provider = _provider(odoo)
    first = await provider.get_ticket("00031")
    assert first is not None and first.ticket.category == "other"
    second = await provider.get_ticket("00031")
    assert second is not None
    assert (second.ticket.status, second.ticket.category) == ("in_progress", "bug")
    await provider.get_ticket("00031")
    assert len(odoo.calls_to("helpdesk.stage", "search_read")) == 2
    assert len(odoo.calls_to("helpdesk.tag", "search_read")) == 2


def _goat_ticket_odoo(messages: list[dict[str, Any]], **record: Any) -> Any:
    rec = ticket_record(
        description='<p>It is empty.</p><img src="/web/image/9?access_token=x">',
        create_date="2026-09-28 09:14:00",
        **record,
    )
    return (
        _detail_odoo()
        .on("helpdesk.ticket", "search_read", lambda kw: [rec])
        .on("mail.message", "search_read", lambda kw: messages)
    )


def _msg(id: int, author: list[Any], body: str, date: str, atts: list[int]) -> dict:
    return {
        "id": id,
        "author_id": author,
        "date": date,
        "body": body,
        "message_type": "comment",
        "is_internal": False,
        "subtype_id": DISCUSSION,
        "attachment_ids": atts,
    }


async def test_goat_ticket_opens_with_the_description_and_its_files() -> None:
    files_message = _msg(60, [100, "Marco"], "", "2026-09-28 09:14:02", [900])
    agent = _msg(62, [300, "Lena"], "<p>Looking</p>", "2026-09-28 11:02:00", [])
    odoo = _goat_ticket_odoo([files_message, agent])
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    (call,) = odoo.calls_to("helpdesk.ticket", "search_read")
    assert "description" in call["fields"]
    first, second = detail.messages
    assert first.id == 60  # the files message's id, merged
    assert (
        (first.author_contact_id, first.author_name, first.is_agent)
        == (
            100,
            "Marco",  # the partner's plain name (the ticket's many2one says "Marco Albrecht")
            False,
        )
    )
    assert first.body_html == "<p>It is empty.</p>"  # Odoo image stripped
    assert first.created_at.isoformat() == "2026-09-28T09:14:00+00:00"
    assert [a.id for a in first.attachments] == [900]
    assert second.id == 62
    # unchanged: latest message (read markers) and the downloadable files
    assert detail.ticket.latest_message_id == 62
    assert detail.visible_attachment_ids == frozenset({900})


async def test_goat_ticket_without_files_gets_a_message_with_id_zero() -> None:
    reply = _msg(60, [100, "Marco"], "<p>More</p>", "2026-09-28 09:20:00", [900])
    odoo = _goat_ticket_odoo([reply])
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert [m.id for m in detail.messages] == [0, 60]
    assert detail.messages[0].attachments == ()
    assert detail.messages[1].attachments[0].id == 900
    assert detail.ticket.latest_message_id == 60


async def test_a_late_files_only_reply_is_not_merged_into_the_description() -> None:
    late = _msg(60, [100, "Marco"], "<p><br></p>", "2026-09-29 09:00:00", [900])
    detail = await _provider(_goat_ticket_odoo([late])).get_ticket("00031")
    assert detail is not None
    assert [m.id for m in detail.messages] == [0, 60]


async def test_email_tickets_get_no_description_message() -> None:
    first = _msg(60, [100, "Marco"], "<p>Hi by mail</p>", "2026-09-28 09:14:00", [])
    odoo = _goat_ticket_odoo([first], x_goat_request_id=False)
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert [m.id for m in detail.messages] == [60]
    assert detail.ticket.via == "email"


async def test_updated_at_is_the_latest_visible_activity_not_write_date() -> None:
    reply = _msg(60, [300, "Lena"], "<p>x</p>", "2026-09-29 08:00:00", [])
    odoo = _goat_ticket_odoo([reply], write_date="2026-09-30 23:00:00")
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert detail.ticket.updated_at.isoformat() == "2026-09-29T08:00:00+00:00"
    quiet = await _provider(_goat_ticket_odoo([])).get_ticket("00031")
    assert quiet is not None
    assert quiet.ticket.updated_at == quiet.ticket.created_at


async def test_upload_that_times_out_is_reported_not_raised() -> None:
    def upload(kw: dict) -> list[int]:
        if kw["vals_list"][0]["name"] == "slow.bin":
            raise SupportUnavailable("timeout")
        return [801]

    odoo = (
        base_odoo()
        .on("ir.attachment", "create", upload)
        .on("ir.actions.server", "run", lambda kw: {"goat_message_id": 77})
    )
    result = await _provider(odoo).post_message(
        31,
        100,
        "",
        [
            UploadedFile("a.png", "image/png", b"PNG"),
            UploadedFile("slow.bin", "application/octet-stream", b"x"),
        ],
    )
    assert (result.message_id, result.failed_files) == (77, ("slow.bin",))


async def test_get_unknown_ticket_is_none() -> None:
    odoo = base_odoo().on("helpdesk.ticket", "search_read", lambda kw: [])
    assert await _provider(odoo).get_ticket("99999") is None


async def test_create_ticket_writes_stamps_tag_and_priority() -> None:
    odoo = (
        base_odoo(people={100: {"name": "Marco", "staff": False}})
        .on("helpdesk.ticket", "create", lambda kw: [40])
        .on(
            "helpdesk.ticket",
            "read",
            lambda kw: [ticket_record(id=40, ticket_ref="00040", stage_id=[1, "New"])],
        )
    )
    new = NewTicket(
        subject="Heatmap empty",
        description_html="<p>x</p>",
        category="data_issue",
        impact="slowing",
        customer_contact_id=100,
        org_id="org-1",
        user_id="user-1",
        request_id="req-9",
    )
    ticket = await _provider(odoo).create_ticket(new)
    assert ticket.ref == "00040" and ticket.status == "new"
    (call,) = odoo.calls_to("helpdesk.ticket", "create")
    assert call["vals_list"] == [
        {
            "name": "Heatmap empty",
            "team_id": 1,
            "partner_id": 100,
            "description": "<p>x</p>",
            "priority": "1",
            "tag_ids": [[6, 0, [4]]],
            "x_goat_organization_id": "org-1",
            "x_goat_user_id": "user-1",
            "x_goat_request_id": "req-9",
        }
    ]


async def test_post_message_uploads_files_then_runs_the_action() -> None:
    uploads: list[dict] = []

    def upload(kw: dict) -> list[int]:
        vals = kw["vals_list"][0]
        if vals["name"] == "broken.bin":
            raise OdooRejected(400, "odoo.exceptions.ValidationError", "bad file")
        uploads.append(vals)
        return [800 + len(uploads)]

    odoo = (
        base_odoo()
        .on("ir.attachment", "create", upload)
        .on(
            "ir.actions.server",
            "run",
            lambda kw: {"type": "ir.actions.act_window_close", "goat_message_id": 77},
        )
    )
    result = await _provider(odoo).post_message(
        31,
        100,
        "Here you go",
        [
            UploadedFile("a.png", "image/png", b"PNG"),
            UploadedFile("broken.bin", "application/octet-stream", b"x"),
        ],
    )
    assert result.message_id == 77
    assert result.failed_files == ("broken.bin",)
    assert uploads[0]["res_model"] == "helpdesk.ticket" and uploads[0]["res_id"] == 31
    assert base64.b64decode(uploads[0]["datas"]) == b"PNG"
    (run,) = odoo.calls_to("ir.actions.server", "run")
    assert run["ids"] == [1562]
    assert run["context"] == {
        "active_model": "helpdesk.ticket",
        "active_id": 31,
        "active_ids": [31],
        "goat_op": "post",
        "goat_author_id": 100,
        "goat_body_text": "Here you go",
        "goat_attachment_ids": [801],
    }


async def test_rate_goes_through_the_action() -> None:
    odoo = base_odoo().on("ir.actions.server", "run", lambda kw: {"goat_rating_id": 3})
    await _provider(odoo).rate(31, 100, "top", "Thanks")
    (run,) = odoo.calls_to("ir.actions.server", "run")
    assert run["context"]["goat_op"] == "rate"
    assert (run["context"]["goat_rating"], run["context"]["goat_feedback"]) == (
        5,
        "Thanks",
    )


async def test_download_decodes_the_file() -> None:
    odoo = base_odoo().on(
        "ir.attachment",
        "read",
        lambda kw: [
            {
                "id": 900,
                "name": "map.png",
                "mimetype": "image/png",
                "file_size": 3,
                "datas": base64.b64encode(b"PNG").decode(),
            }
        ],
    )
    meta, data = await _provider(odoo).download(900)
    assert (meta.name, data) == ("map.png", b"PNG")


# Odoo's many2one name of an individual is "Company, Name"; the partner's own
# `name` is the plain one. Everywhere a person is shown the plain name is used.
def _prefixed_odoo(messages: list[dict[str, Any]], **record: Any) -> Any:
    people = {
        100: {"name": "Marco Albrecht", "staff": False},
        26: {"name": "Majk Shkurti", "staff": True},
    }
    return (
        _goat_ticket_odoo(messages, partner_id=[100, "Stadt, Marco Albrecht"], **record)
        .on_op("followers", lambda ctx: {"goat_partner_ids": [26]})
        .on("ir.actions.server", "run", action_ops(people=people))
    )


async def test_people_are_shown_with_their_plain_name_not_the_display_name() -> None:
    reply = _msg(62, [26, "Test, Majk Shkurti"], "<p>Hi</p>", "2026-09-28 11:00:00", [])
    odoo = _prefixed_odoo([reply])
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    opening, answer = detail.messages
    assert opening.author_name == "Marco Albrecht"
    assert answer.author_name == "Majk Shkurti"
    assert detail.ticket.customer_name == "Marco Albrecht"
    assert detail.ticket.latest_message_author == "Majk Shkurti"
    assert [f.name for f in detail.followers] == ["Majk Shkurti"]
    # one "people" ask serves authors, followers and the customer
    (ask,) = [c for c in op_calls(odoo, "people") if not c["goat_with_photos"]]
    assert ask["goat_partner_ids"] == [26, 100]


async def test_list_shows_plain_names_for_the_customer_and_latest_author() -> None:
    odoo = (
        base_odoo(
            people={
                100: {"name": "Marco Albrecht", "staff": False},
                26: {"name": "Majk Shkurti", "staff": True},
            }
        )
        .on(
            "helpdesk.ticket",
            "search_read",
            lambda kw: [ticket_record(partner_id=[100, "Stadt, Marco Albrecht"])],
        )
        .on(
            "mail.message",
            "search_read",
            lambda kw: [
                {
                    "id": 70,
                    "res_id": 31,
                    "author_id": [26, "Test, Majk Shkurti"],
                    "date": "2026-09-30 11:02:00",
                    "message_type": "comment",
                    "is_internal": False,
                    "subtype_id": DISCUSSION,
                }
            ],
        )
    )
    (t,) = await _provider(odoo).list_tickets(TicketQuery((100,), None, None, None))
    assert (t.customer_name, t.latest_message_author) == (
        "Marco Albrecht",
        "Majk Shkurti",
    )
    assert len(op_calls(odoo, "people")) == 1


async def test_a_missing_partner_name_falls_back_to_the_many2one_name() -> None:
    reply = _msg(62, [26, "Test, Majk Shkurti"], "<p>Hi</p>", "2026-09-28 11:00:00", [])
    odoo = (
        _goat_ticket_odoo([reply])
        .on_op("followers", lambda ctx: {"goat_partner_ids": []})
        .on(
            "ir.actions.server",
            "run",
            action_ops(people={26: {"name": False, "staff": True}}),
        )
    )
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert detail.messages[-1].author_name == "Test, Majk Shkurti"
    assert detail.ticket.customer_name == "Marco Albrecht"


async def test_agent_name_is_the_users_name_and_empty_when_the_user_is_deleted() -> (
    None
):
    # The bridge cannot read res.users; a user's many2one name is already the
    # partner's plain name (no company prefix), so it is used as it comes.
    odoo = _prefixed_odoo([], user_id=[5, "Majk Shkurti"])
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None and detail.ticket.agent_name == "Majk Shkurti"
    assert odoo.calls_to("res.users", "read") == []  # never asked for the agent
    gone = await _provider(_prefixed_odoo([], user_id=False)).get_ticket("00031")
    assert gone is not None and gone.ticket.agent_name is None


async def test_a_message_whose_author_was_deleted_is_unknown_not_an_agent() -> None:
    orphan = _msg(62, False, "<p>Hi</p>", "2026-09-28 11:00:00", [])  # type: ignore[arg-type]
    detail = await _provider(_prefixed_odoo([orphan])).get_ticket("00031")
    assert detail is not None
    known, unknown = detail.messages
    assert known.author_known and known.author_name == "Marco Albrecht"
    assert (unknown.author_known, unknown.author_name, unknown.is_agent) == (
        False,
        "",
        False,
    )
    assert unknown.author_contact_id is None


async def test_create_ticket_names_the_customer_plainly() -> None:
    odoo = (
        base_odoo(people={100: {"name": "Marco Albrecht", "staff": False}})
        .on("helpdesk.ticket", "create", lambda kw: [77])
        .on(
            "helpdesk.ticket",
            "read",
            lambda kw: [
                ticket_record(id=77, partner_id=[100, "Stadt, Marco Albrecht"])
            ],
        )
    )
    new = NewTicket("S", "<p>d</p>", "bug", None, 100, None, "u", "r")
    ticket = await _provider(odoo).create_ticket(new)
    assert ticket.customer_name == "Marco Albrecht"


async def test_contacts_exist_asks_the_server_action() -> None:
    odoo = base_odoo(goat_contacts=(100,))
    assert await _provider(odoo).contacts_exist([100, 101, 100]) == {100}
    (ask,) = op_calls(odoo, "exist")
    assert ask["goat_partner_ids"] == [100, 101]
    assert await _provider(odoo).contacts_exist([]) == set()
    assert len(op_calls(odoo, "exist")) == 1


# ----------------------------------------------------------------- staff photos
JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 40
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 40
WEBP = b"RIFF\x00\x00\x00\x00WEBPVP8 " + b"\x00" * 40
SVG = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="4"/></svg>'


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _photo_odoo(photos: dict[int, Any]) -> Any:
    """_detail_odoo, with image_128 answered from `photos` (False = none)."""
    return _detail_odoo(photos=photos)


def _photo_reads(odoo: Any) -> list[dict[str, Any]]:
    return [c for c in op_calls(odoo, "people") if c["goat_with_photos"]]


async def test_staff_photo_is_inlined_and_customers_never_get_one() -> None:
    # 100 (Marco) is a customer with a photo; 300 (Lena) is staff
    odoo = _photo_odoo({100: _b64(JPEG), 300: _b64(JPEG)})
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert detail.avatars == {300: f"data:image/jpeg;base64,{_b64(JPEG)}"}
    (call,) = _photo_reads(odoo)
    assert call["goat_partner_ids"] == [300]


async def test_photo_type_comes_from_the_bytes() -> None:
    for data, mime in ((PNG, "image/png"), (WEBP, "image/webp"), (JPEG, "image/jpeg")):
        detail = await _provider(_photo_odoo({300: _b64(data)})).get_ticket("00031")
        assert detail is not None
        assert detail.avatars == {300: f"data:{mime};base64,{_b64(data)}"}


@pytest.mark.parametrize(
    "value", [False, "", _b64(SVG), _b64(b"GIF89a" + b"\x00" * 10), "not base64!!"]
)
async def test_empty_svg_and_unknown_photos_are_left_out(value: Any) -> None:
    detail = await _provider(_photo_odoo({300: value})).get_ticket("00031")
    assert detail is not None and detail.avatars == {}


async def test_photo_over_64_kb_is_skipped() -> None:
    big = JPEG + b"\x00" * (64 * 1024)
    ok = JPEG + b"\x00" * (64 * 1024 - len(JPEG))
    assert len(ok) == 64 * 1024
    detail = await _provider(_photo_odoo({300: _b64(big)})).get_ticket("00031")
    assert detail is not None and detail.avatars == {}
    detail = await _provider(_photo_odoo({300: _b64(ok)})).get_ticket("00031")
    assert detail is not None and 300 in detail.avatars


async def test_photos_and_missing_photos_are_cached() -> None:
    extra = [
        {
            "id": 63,
            "author_id": [26, "Majk"],
            "date": "2026-09-28 12:00:00",
            "body": "<p>Me too</p>",
            "message_type": "comment",
            "is_internal": False,
            "subtype_id": DISCUSSION,
            "attachment_ids": [],
        }
    ]
    # the same messages plus one by staff partner 26, who has no photo
    odoo = _detail_odoo(extra, photos={300: _b64(JPEG)})
    provider = _provider(odoo)
    first = await provider.get_ticket("00031")
    second = await provider.get_ticket("00031")
    assert first is not None and second is not None
    assert set(first.avatars) == set(second.avatars) == {300}
    (call,) = _photo_reads(odoo)  # one ask for both partners, none the second time
    assert call["goat_partner_ids"] == [26, 300]


async def test_cache_expires_after_an_hour(monkeypatch: pytest.MonkeyPatch) -> None:
    now = [1000.0]
    odoo = _photo_odoo({300: _b64(JPEG)})
    provider = _provider(odoo)
    from core.support.throttle import TTLCache

    provider._avatars = TTLCache(now=lambda: now[0])
    await provider.get_ticket("00031")
    now[0] += 3599
    await provider.get_ticket("00031")
    assert len(_photo_reads(odoo)) == 1
    now[0] += 2
    await provider.get_ticket("00031")
    assert len(_photo_reads(odoo)) == 2


async def test_a_failed_photo_read_does_not_break_the_ticket_nor_get_cached() -> None:
    odoo = _photo_odoo({300: _b64(JPEG)})
    ok_run = odoo._handlers[("ir.actions.server", "run")]
    failing = [True]

    def run(kw: dict[str, Any]) -> Any:
        if kw["context"].get("goat_with_photos") and failing[0]:
            raise OdooRejected(403, "odoo.exceptions.UserError", "no")
        return ok_run(kw)

    odoo.on("ir.actions.server", "run", run)
    provider = _provider(odoo)
    detail = await provider.get_ticket("00031")
    assert detail is not None and detail.avatars == {}
    failing[0] = False
    detail = await provider.get_ticket("00031")
    assert detail is not None and 300 in detail.avatars


async def test_no_staff_author_means_no_photo_read() -> None:
    odoo = _photo_odoo({})
    odoo.on(
        "mail.message",
        "search_read",
        lambda kw: [
            {
                "id": 60,
                "author_id": [100, "Marco"],
                "date": "2026-09-28 09:14:00",
                "body": "<p>Hi</p>",
                "message_type": "comment",
                "is_internal": False,
                "subtype_id": DISCUSSION,
                "attachment_ids": [],
            }
        ],
    )
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None and detail.avatars == {}
    assert _photo_reads(odoo) == []


# ------------------------------------------------- staff who left (archived/deleted)
# Odoo recomputes partner_share from active users only: the partner of an archived
# or deleted staff user is a share partner. The server action's ops know better.
FORMER = 400  # former staff: partner_share True, staff for the server action


def _former_staff_odoo(staff: tuple[int, ...] = (FORMER,)) -> Any:
    people = {
        100: {"name": "Marco", "staff": False, "photo": _b64(JPEG)},
        FORMER: {"name": "Lena (left)", "staff": False, "photo": _b64(JPEG)},
        26: {"name": "Majk", "staff": True, "photo": _b64(JPEG)},
    }
    return (
        base_odoo(staff=staff, people=people)
        .on(
            "helpdesk.ticket",
            "search_read",
            lambda kw: [ticket_record(x_goat_request_id=False)],
        )
        .on(
            "mail.message",
            "search_read",
            lambda kw: sorted(
                [
                    {
                        **_msg(
                            60, [100, "Marco"], "<p>Hi</p>", "2026-09-28 09:14:00", []
                        ),
                        "res_id": 31,
                    },
                    {
                        **_msg(
                            61,
                            [FORMER, "Lena"],
                            "<p>On it</p>",
                            "2026-09-28 10:00:00",
                            [],
                        ),
                        "res_id": 31,
                    },
                ],
                key=lambda m: m["id"],
                reverse=kw["order"] == "id desc",
            ),
        )
        .on_op("followers", lambda ctx: {"goat_partner_ids": [100, FORMER, 26]})
    )


def _staff_asks(odoo: Any) -> list[list[int]]:
    return [
        kw["context"]["goat_partner_ids"]
        for kw in odoo.calls_to("ir.actions.server", "run")
        if kw["context"].get("goat_op") == "staff"
    ]


async def test_former_staff_stay_agents_internal_followers_with_a_photo() -> None:
    odoo = _former_staff_odoo()
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None
    assert [(m.author_contact_id, m.is_agent) for m in detail.messages] == [
        (100, False),
        (FORMER, True),
    ]
    assert detail.ticket.latest_message_is_agent is True
    assert {(f.contact_id, f.is_internal) for f in detail.followers} == {
        (100, False),
        (FORMER, True),
        (26, True),
    }
    assert set(detail.avatars) == {FORMER}
    # one "people" ask names everyone and tells staff apart
    assert op_calls(odoo, "people")[0]["goat_partner_ids"] == [26, 100, FORMER]
    assert _staff_asks(odoo) == []


async def test_list_counts_a_reply_of_former_staff_as_an_agent_reply() -> None:
    odoo = _former_staff_odoo()
    (t,) = await _provider(odoo).list_tickets(TicketQuery((100,), None, None, None))
    assert t.latest_message_id == 61 and t.latest_message_is_agent is True


async def test_people_answers_fill_the_staff_cache() -> None:
    odoo = _former_staff_odoo()
    provider = _provider(odoo)
    await provider.get_ticket("00031")
    assert await provider._staff([100, FORMER, 26]) == {FORMER, 26}
    assert _staff_asks(odoo) == []


async def test_a_failed_people_lookup_fails_the_read() -> None:
    odoo = _former_staff_odoo()

    def down(kw: dict[str, Any]) -> Any:
        raise SupportUnavailable("timeout")

    odoo.on("ir.actions.server", "run", down)
    with pytest.raises(SupportUnavailable):
        await _provider(odoo).get_ticket("00031")
    with pytest.raises(SupportUnavailable):
        await _provider(odoo).find_contacts_by_email(["lena@p4b.de"])
    with pytest.raises(SupportUnavailable):
        await _provider(odoo).contacts_exist([100])


async def test_a_missing_server_action_makes_the_contact_lookups_unavailable() -> None:
    odoo = base_odoo().on("ir.actions.server", "search", lambda kw: [])
    with pytest.raises(SupportUnavailable):
        await _provider(odoo).contacts_exist([100])
    with pytest.raises(SupportUnavailable):
        await _provider(odoo).find_contacts_by_email(["a@x.de"])


# ------------------------------------------------------------ assigned agent
def _agent_asks(odoo: Any) -> list[dict[str, Any]]:
    return [
        kw["context"]
        for kw in odoo.calls_to("ir.actions.server", "run")
        if kw["context"]["goat_op"] == "agent"
    ]


def _agent_odoo(
    agent_partner: int | None = 300, staff: tuple[int, ...] = (300,), **record: Any
) -> Any:
    """_photo_odoo whose only team message is none: the agent has not written yet."""
    odoo = _photo_odoo({300: _b64(JPEG)})
    odoo.on("mail.message", "search_read", lambda kw: [])
    odoo.on(
        "ir.actions.server",
        "run",
        action_ops(staff, agent_partner, people=_detail_people({300: _b64(JPEG)})),
    )
    odoo.on("helpdesk.ticket", "search_read", lambda kw: [ticket_record(**record)])
    return odoo


async def test_the_assigned_agent_is_known_and_has_a_photo_before_they_write() -> None:
    odoo = _agent_odoo()
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None and detail.messages == ()
    assert detail.agent_contact_id == 300
    assert detail.avatars == {300: f"data:image/jpeg;base64,{_b64(JPEG)}"}
    (ask,) = _agent_asks(odoo)
    assert (ask["active_model"], ask["active_id"]) == ("helpdesk.ticket", 31)


async def test_the_agent_partner_is_cached_per_ticket_and_handler() -> None:
    odoo = _agent_odoo()
    provider = _provider(odoo)
    await provider.get_ticket("00031")
    await provider.get_ticket("00031")
    assert len(_agent_asks(odoo)) == 1
    # reassigned: the new handler is asked, not served from the old answer
    odoo.on(
        "helpdesk.ticket",
        "search_read",
        lambda kw: [ticket_record(user_id=[11, "Jonas"])],
    )
    await provider.get_ticket("00031")
    assert len(_agent_asks(odoo)) == 2


async def test_the_agent_partner_cache_expires_after_ten_minutes() -> None:
    from core.support.throttle import TTLCache

    odoo = _agent_odoo()
    provider = _provider(odoo)
    now = [0.0]
    provider._agent_partners = TTLCache(now=lambda: now[0])
    await provider.get_ticket("00031")
    now[0] = 599.0
    await provider.get_ticket("00031")
    assert len(_agent_asks(odoo)) == 1
    now[0] = 601.0
    await provider.get_ticket("00031")
    assert len(_agent_asks(odoo)) == 2


async def test_an_unassigned_ticket_asks_nothing() -> None:
    odoo = _agent_odoo(user_id=False)
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None and detail.agent_contact_id is None
    assert _agent_asks(odoo) == []
    assert detail.avatars == {}


async def test_a_handler_without_a_partner_gives_no_agent() -> None:
    odoo = _agent_odoo(agent_partner=None)
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None and detail.agent_contact_id is None


@pytest.mark.parametrize(
    "error",
    [
        OdooRejected(403, "odoo.exceptions.UserError", "unknown ticket"),
        SupportUnavailable("odoo down"),
    ],
)
async def test_a_failed_agent_lookup_falls_back_silently_and_is_not_cached(
    error: Exception,
) -> None:
    odoo = _agent_odoo()
    provider = _provider(odoo)
    ops = odoo._handlers[("ir.actions.server", "run")]
    failing = [True]

    def run(kw: dict[str, Any]) -> Any:
        if kw["context"]["goat_op"] == "agent" and failing[0]:
            raise error
        return ops(kw)

    odoo.on("ir.actions.server", "run", run)
    detail = await provider.get_ticket("00031")
    assert detail is not None and detail.agent_contact_id is None
    failing[0] = False
    detail = await provider.get_ticket("00031")
    assert detail is not None and detail.agent_contact_id == 300


async def test_an_assigned_handler_who_is_not_staff_gets_no_photo() -> None:
    odoo = _agent_odoo(staff=())
    detail = await _provider(odoo).get_ticket("00031")
    assert detail is not None and detail.agent_contact_id == 300
    assert detail.avatars == {}
    assert _photo_reads(odoo) == []


async def test_a_server_action_without_the_agent_op_is_not_asked_for_ten_minutes() -> (
    None
):
    from core.support.throttle import TTLCache

    odoo = _agent_odoo()
    provider = _provider(odoo)
    now = [0.0]
    provider._agent_partners = TTLCache(now=lambda: now[0])
    staff = odoo._handlers[("ir.actions.server", "run")]

    def run(kw: dict[str, Any]) -> Any:
        if kw["context"]["goat_op"] == "agent":
            raise OdooRejected(403, "odoo.exceptions.UserError", "unknown operation")
        return staff(kw)

    odoo.on("ir.actions.server", "run", run)
    for _ in range(3):
        detail = await provider.get_ticket("00031")
        assert detail is not None and detail.agent_contact_id is None
    assert len(_agent_asks(odoo)) == 1
    # another ticket, same answer: the op is missing, not the ticket
    odoo.on(
        "helpdesk.ticket",
        "search_read",
        lambda kw: [ticket_record(id=32, user_id=[11, "J"])],
    )
    await provider.get_ticket("00032")
    assert len(_agent_asks(odoo)) == 1
    # set up again later: asked again once the ten minutes are over
    odoo.on("ir.actions.server", "run", staff)
    now[0] = 601.0
    detail = await provider.get_ticket("00032")
    assert detail is not None and detail.agent_contact_id == 300
    assert len(_agent_asks(odoo)) == 2


async def test_staff_lookups_are_split_into_batches_the_action_accepts() -> None:
    odoo = base_odoo(staff=(5, 1500))
    provider = _provider(odoo)
    staff = await provider._staff(range(1, 2501))
    assert staff == {5, 1500}
    asks = [
        kw["context"]["goat_partner_ids"]
        for kw in odoo.calls_to("ir.actions.server", "run")
    ]
    assert [len(a) for a in asks] == [1000, 1000, 500]
    assert sorted(p for a in asks for p in a) == list(range(1, 2501))


async def test_a_refused_parent_company_is_its_own_error() -> None:
    from core.support.errors import SupportCompanyRefused

    def run(kw: dict[str, Any]) -> Any:
        message = (
            "invalid parent company"
            if kw["context"]["goat_parent_id"]
            else "invalid contact"
        )
        raise OdooRejected(403, "odoo.exceptions.UserError", message)

    provider = _provider(base_odoo().on("ir.actions.server", "run", run))
    with pytest.raises(SupportCompanyRefused):
        await provider.create_contact(name="A", email="a@x.de", lang="en", company_id=5)
    with pytest.raises(OdooRejected) as other:
        await provider.create_contact(
            name="A", email="a@x.de", lang="en", company_id=None
        )
    assert not isinstance(other.value, SupportCompanyRefused)


async def test_create_contact_sends_a_clean_name_the_action_accepts() -> None:
    odoo = base_odoo().on("ir.actions.server", "run", lambda kw: {"goat_contact_id": 1})
    provider = _provider(odoo)
    await provider.create_contact(
        name="Anna\tKeller\r\n", email="a@x.de", lang="en", company_id=None
    )
    await provider.create_contact(
        name="x" * 250, email="b@x.de", lang="en", company_id=None
    )
    await provider.create_contact(name="\n", email="c@x.de", lang="en", company_id=None)
    names = [
        kw["context"]["goat_name"] for kw in odoo.calls_to("ir.actions.server", "run")
    ]
    assert names == ["Anna Keller", "x" * 200, "c@x.de"]


# ------------------------------------------------------------------- rating
def _rating_odoo(value: Any) -> Any:
    return base_odoo().on_op("my_rating", lambda ctx: {"goat_rating": value})


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1.0, "ko"), (3.0, "ok"), (5.0, "top"), (0.0, None), (2.0, None), (False, None)],
)
async def test_my_rating_maps_odoos_values(value: Any, expected: str | None) -> None:
    odoo = _rating_odoo(value)
    assert await _provider(odoo).my_rating(31, 100) == expected


async def test_my_rating_asks_for_this_contacts_consumed_rating_of_this_ticket() -> (
    None
):
    odoo = _rating_odoo(False)
    assert await _provider(odoo).my_rating(31, 100) is None
    (ask,) = op_calls(odoo, "my_rating")
    assert (ask["active_model"], ask["active_id"]) == ("helpdesk.ticket", 31)
    assert ask["goat_partner_id"] == 100


async def test_a_staff_email_is_its_own_error() -> None:
    from core.support.errors import SupportStaffEmail

    def run(kw: dict[str, Any]) -> Any:
        raise OdooRejected(422, "odoo.exceptions.UserError", "email belongs to staff")

    provider = _provider(base_odoo().on("ir.actions.server", "run", run))
    with pytest.raises(SupportStaffEmail):
        await provider.create_contact(
            name="Lena", email="lena@plan4better.example", lang="en", company_id=None
        )
