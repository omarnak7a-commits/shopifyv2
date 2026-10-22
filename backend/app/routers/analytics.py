from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import TryOnSession, Product, User
from app.schemas import AnalyticsSummary, TryOnSessionOut
from app.dependencies import require_store_owner

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/{store_id}", response_model=AnalyticsSummary)
def get_analytics(
    store_id: str,
    user: User = Depends(require_store_owner),
    db: Session = Depends(get_db),
):
    sessions = db.query(TryOnSession).filter(TryOnSession.store_id == store_id).all()
    total = len(sessions)
    successful = sum(1 for s in sessions if s.status == "completed")
    failed = sum(1 for s in sessions if s.status == "failed")

    product_counts: dict[str, int] = {}
    for s in sessions:
        product_counts[s.product_id] = product_counts.get(s.product_id, 0) + 1

    most_tried = None
    if product_counts:
        top_pid = max(product_counts, key=product_counts.get)
        product = db.query(Product).filter(Product.id == top_pid).first()
        most_tried = {
            "id": top_pid,
            "name": product.name if product else "Unknown",
            "count": product_counts[top_pid],
        }

    recent = sorted(sessions, key=lambda s: s.created_at, reverse=True)[:10]

    return AnalyticsSummary(
        totalTryOns=total,
        successful=successful,
        failed=failed,
        mostTriedProduct=most_tried,
        recentSessions=[TryOnSessionOut.from_orm_session(s) for s in recent],
    )
