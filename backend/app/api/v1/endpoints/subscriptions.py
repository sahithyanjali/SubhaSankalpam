from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.middleware.auth import get_current_active_user
from app.models.subscription import Payment, PaymentStatus, SubscriptionPlan, UserSubscription
from app.models.user import User
from app.schemas.subscription import PaymentCreate, PaymentResponse, PlanResponse, SubscribeRequest, SubscriptionResponse

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=list[PlanResponse])
async def get_plans(db: AsyncSession = Depends(get_db)):
    """Get all available subscription plans: Free, Silver, Gold, Platinum."""
    result = await db.execute(
        select(SubscriptionPlan).where(SubscriptionPlan.is_active.is_(True)).order_by(SubscriptionPlan.price)
    )
    return result.scalars().all()


@router.get("/my-subscription", response_model=SubscriptionResponse)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's subscription status."""
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="No active subscription")
    return subscription


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    data: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Subscribe to a plan (Free/Silver/Gold/Platinum)."""
    plan_result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == data.plan_id))
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check existing subscription
    existing = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    current_sub = existing.scalar_one_or_none()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=plan.duration_days)

    if current_sub:
        current_sub.plan_id = plan.id
        current_sub.starts_at = now
        current_sub.expires_at = expires_at
        current_sub.is_active = True
        subscription = current_sub
    else:
        subscription = UserSubscription(
            user_id=current_user.id,
            plan_id=plan.id,
            starts_at=now,
            expires_at=expires_at,
        )
        db.add(subscription)

    await db.commit()
    await db.refresh(subscription)

    # Eagerly load plan
    plan_result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == subscription.plan_id))
    subscription.plan = plan_result.scalar_one()

    return subscription


@router.post("/payment", response_model=PaymentResponse)
async def record_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Record a payment for subscription."""
    sub_result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == current_user.id)
    )
    subscription = sub_result.scalar_one_or_none()
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")

    payment = Payment(
        subscription_id=subscription.id,
        user_id=current_user.id,
        amount=data.amount,
        gateway_order_id=data.gateway_order_id,
        gateway_payment_id=data.gateway_payment_id,
        status=PaymentStatus.COMPLETED,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment
