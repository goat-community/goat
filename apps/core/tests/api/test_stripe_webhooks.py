"""Stripe events for a customer without an organization.

Deleting an organization permanently leaves its Stripe customer in place;
whoever deleted it cancels the customer in Stripe. Until then Stripe keeps
sending that customer's events, and none may email its former owner.

A customer is also without an organization for a moment at signup: core
creates the customer and its subscription before it saves the organization,
so Stripe's first events can arrive before the row exists. Those keep doing
their Stripe-side work.
"""

import logging
from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import core.endpoints.v2.webhooks as webhooks
import pytest
from core.core.config import settings
from core.deps.stripe import stripe_webhook_payload
from core.main import app
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import make_organization

LISTENER = f"{settings.API_V2_STR}/webhooks/stripe/listener"


class _Recorder:
    """Stands in for the Stripe module and `send_email`, recording each call."""

    def __init__(self) -> None:
        self.stripe_calls: list[str] = []
        self.emails: list[str] = []

        def call(name: str, result: Any) -> Any:
            def record(*args: Any, **kwargs: Any) -> Any:
                self.stripe_calls.append(name)
                return result

            return record

        subscription = {"id": "sub_1", "status": "trialing", "items": []}
        self.stripe = SimpleNamespace(
            Customer=SimpleNamespace(
                retrieve=call("Customer.retrieve", {"email": "owner@example.org"})
            ),
            Subscription=SimpleNamespace(
                retrieve=call("Subscription.retrieve", subscription),
                modify=call("Subscription.modify", None),
            ),
            PaymentIntent=SimpleNamespace(
                retrieve=call(
                    "PaymentIntent.retrieve", SimpleNamespace(payment_method="pm_1")
                )
            ),
            Product=SimpleNamespace(
                retrieve=call("Product.retrieve", {"metadata": {}})
            ),
        )

    def send_email(self, email_to: str, **kwargs: Any) -> None:
        self.emails.append(email_to)


@pytest.fixture
def recorder(monkeypatch: pytest.MonkeyPatch) -> _Recorder:
    recorder = _Recorder()
    monkeypatch.setattr(webhooks, "get_stripe", lambda: recorder.stripe)
    monkeypatch.setattr(webhooks, "send_email", recorder.send_email)
    return recorder


@pytest.fixture
def deliver() -> Iterator[Any]:
    """Posts an event to the listener as if Stripe had signed it."""

    async def _deliver(event_type: str, data: dict[str, Any]) -> Any:
        event = {"type": event_type, "data": {"object": data}}
        app.dependency_overrides[stripe_webhook_payload] = lambda: event
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(LISTENER)

    yield _deliver
    app.dependency_overrides.pop(stripe_webhook_payload, None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("event_type", "data"),
    [
        ("customer.subscription.trial_will_end", {"default_payment_method": None}),
        ("customer.subscription.deleted", {}),
    ],
)
async def test_no_email_goes_out_for_a_customer_without_organization(
    event_type: str,
    data: dict[str, Any],
    recorder: _Recorder,
    deliver: Any,
) -> None:
    customer = f"cus_{uuid4().hex[:12]}"

    response = await deliver(event_type, {**data, "customer": customer})

    assert response.status_code == 200, response.text
    assert recorder.emails == []


@pytest.mark.asyncio
async def test_the_trial_email_is_skipped_with_an_info_log(
    recorder: _Recorder,
    deliver: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    customer = f"cus_{uuid4().hex[:12]}"
    caplog.set_level(logging.INFO, logger=webhooks.__name__)

    await deliver(
        "customer.subscription.trial_will_end",
        {"default_payment_method": None, "customer": customer},
    )

    assert "Customer.retrieve" not in recorder.stripe_calls
    assert any(
        customer in record.getMessage() and record.levelno == logging.INFO
        for record in caplog.records
    ), caplog.text


@pytest.mark.asyncio
async def test_a_signup_payment_before_the_organization_is_saved_still_counts(
    recorder: _Recorder,
    deliver: Any,
) -> None:
    """The paid first invoice still makes its payment method the default."""
    customer = f"cus_{uuid4().hex[:12]}"

    response = await deliver(
        "invoice.payment_succeeded",
        {
            "billing_reason": "subscription_create",
            "subscription": "sub_1",
            "payment_intent": "pi_1",
            "customer": customer,
        },
    )

    assert response.status_code == 200, response.text
    assert "Subscription.modify" in recorder.stripe_calls
    assert recorder.emails == []


@pytest.mark.asyncio
async def test_a_customer_with_an_organization_is_still_told_about_its_trial(
    db_session: AsyncSession,
    recorder: _Recorder,
    deliver: Any,
) -> None:
    customer = f"cus_{uuid4().hex[:12]}"
    db_session.add(make_organization(id=uuid4(), stripe_id=customer))
    await db_session.commit()

    response = await deliver(
        "customer.subscription.trial_will_end",
        {"default_payment_method": None, "customer": customer},
    )

    assert response.status_code == 200, response.text
    assert recorder.emails == ["owner@example.org"]
