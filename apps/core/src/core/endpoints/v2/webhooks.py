from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.core.config import settings
from core.crud.crud_organization import organization as crud_organization
from core.deps.stripe import get_stripe, stripe_webhook_payload
from core.endpoints.deps import get_db
from core.schemas.email import EmailTemplateContent
from core.utils.email import send_email
from core.utils.i18n import trans as _

router = APIRouter()


@router.post("/stripe/listener", response_class=JSONResponse)
async def listen_stripe_webhooks(
    *,
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(stripe_webhook_payload),
) -> None:  # noqa: ANN201
    event_type = payload.get("type")
    data_object = payload["data"]["object"]  # type: ignore
    stripe = get_stripe()
    if (
        event_type == "invoice.payment_succeeded"
        or event_type == "customer.subscription.created"
    ):
        if (
            data_object.get("billing_reason") == "subscription_create"
            or data_object.get("collection_method") == "send_invoice"
        ):
            if event_type == "invoice.payment_succeeded":
                subscription = stripe.Subscription.retrieve(data_object["subscription"])
            else:
                subscription = data_object
            organization = await crud_organization.get_by_key(
                db, key="stripe_id", value=data_object["customer"]
            )

            if organization and len(organization) > 0 and subscription:
                plan_name = None
                organization = organization[0]
                organization.suspended = False
                if subscription["status"] == "trialing":
                    organization.on_trial = True
                else:
                    organization.on_trial = False
                for item in subscription["items"]:
                    product = stripe.Product.retrieve(item["price"]["product"])
                    plan_name = product["metadata"].get("plan_name")
                    editors = product["metadata"].get("editors")
                    projects = product["metadata"].get("projects")
                    viewers = product["metadata"].get("viewers")
                    credits = product["metadata"].get("credits")
                    storage = product["metadata"].get("storage")
                    if plan_name:
                        organization.plan_name = plan_name
                    if editors:
                        organization.total_editors = int(editors)
                    if projects:
                        organization.total_projects = int(projects)
                    if viewers:
                        organization.total_viewers = int(viewers)
                    if credits:
                        organization.total_credits = int(credits)
                    if storage:
                        organization.total_storage = int(storage)

            await db.commit()
            payment_intent_id = data_object.get("payment_intent")
            if payment_intent_id:
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                subscription_id = subscription["id"]
                stripe.Subscription.modify(
                    subscription_id,
                    default_payment_method=payment_intent.payment_method,
                )
    elif event_type == "invoice.payment_failed":
        print("Invoice payment failed: for customer %s" % data_object["customer"])
    elif event_type == "customer.subscription.trial_will_end":
        if data_object["default_payment_method"] is None:
            email_content = EmailTemplateContent(
                artwork_url=f"{settings.email_artwork_url}/img/email/subscription_about_to_end.png",
                title=_("Your trial is about to end"),
                message=_("Please reach out to us to continue using GOAT."),
                action_label=(_("Contact us") if settings.EMAIL_CONTACT_URL else None),
                action_url=settings.EMAIL_CONTACT_URL,
            )
            customer = stripe.Customer.retrieve(data_object["customer"])
            send_email(
                email_to=customer["email"],
                subject=_("GOAT - Your trial is about to end"),
                environment=email_content.model_dump(),
            )
        print("Trial will end: %s" % data_object["customer"])
    elif event_type == "customer.subscription.deleted":
        organization = await crud_organization.get_by_key(
            db, key="stripe_id", value=data_object["customer"]
        )
        if organization and len(organization) > 0:
            organization = organization[0]
            organization.suspended = True
            organization.on_trial = False
            await db.commit()
            email_content = EmailTemplateContent(
                artwork_url=f"{settings.email_artwork_url}/img/email/organization_suspended.png",
                title=_("Your account is suspended"),
                message=_("Please reach out to us to reactivate your subscription."),
                action_label=(_("Contact us") if settings.EMAIL_CONTACT_URL else None),
                action_url=settings.EMAIL_CONTACT_URL,
            )
            customer = stripe.Customer.retrieve(data_object["customer"])
            send_email(
                email_to=customer["email"],
                subject=_("GOAT - Your subscription was deleted"),
                environment=email_content.model_dump(),
            )
        print("Subscription deleted: %s" % data_object["customer"])
