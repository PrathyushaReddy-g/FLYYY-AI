from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_protected_db
from app.models import ProtectedCustomer, User
from app.schemas import CustomerListResponse, ProtectedCustomerResponse
from app.security.auth import get_current_user

router = APIRouter(prefix="/customers", tags=["Protected Customers"])

@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = None,
    protected_db: Session = Depends(get_protected_db),
    current_user: User = Depends(get_current_user)
):
    query = protected_db.query(ProtectedCustomer)

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            (ProtectedCustomer.customer_id.ilike(s)) |
            (ProtectedCustomer.email_token.ilike(s)) |
            (ProtectedCustomer.city.ilike(s)) |
            (ProtectedCustomer.segment.ilike(s))
        )

    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(ProtectedCustomer.customer_id).offset(offset).limit(page_size).all()

    items = [
        ProtectedCustomerResponse(
            customer_id=c.customer_id,
            name=c.name_token,
            email=c.email_token,
            mobile=c.mobile_fpe,
            city=c.city,
            segment=c.segment,
            protection_version=c.protection_version,
            created_at=c.created_at.isoformat() if c.created_at else None
        )
        for c in records
    ]

    return CustomerListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{customer_id}", response_model=ProtectedCustomerResponse)
def get_customer(
    customer_id: str,
    protected_db: Session = Depends(get_protected_db),
    current_user: User = Depends(get_current_user)
):
    customer = protected_db.query(ProtectedCustomer).filter(
        ProtectedCustomer.customer_id == customer_id
    ).first()

    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CUSTOMER_NOT_FOUND")

    return ProtectedCustomerResponse(
        customer_id=customer.customer_id,
        name=customer.name_token,
        email=customer.email_token,
        mobile=customer.mobile_fpe,
        city=customer.city,
        segment=customer.segment,
        protection_version=customer.protection_version,
        created_at=customer.created_at.isoformat() if customer.created_at else None
    )
