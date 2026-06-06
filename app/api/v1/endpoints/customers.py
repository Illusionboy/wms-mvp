from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.services.auth import CurrentUser
from app.db.session import get_db_session
from app.models.customer import Customer
from app.schemas.inventory import CustomerCreate, CustomerRead

router = APIRouter()


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_auth)])
async def create_customer(
    payload: CustomerCreate,
    session: AsyncSession = Depends(get_db_session),
) -> CustomerRead:
    customer = Customer(name=payload.name, contact_info=payload.contact_info)
    session.add(customer)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer name already exists.",
        ) from exc
    await session.refresh(customer)
    return CustomerRead.model_validate(customer)


@router.get("", response_model=list[CustomerRead])
async def list_customers(
    session: AsyncSession = Depends(get_db_session),
) -> list[Customer]:
    result = await session.scalars(select(Customer).order_by(Customer.name.asc()))
    return list(result.all())


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Customer:
    customer = await session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found.")
    return customer
