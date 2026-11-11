from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.portfolio import (
    PortfolioAnswerOut,
    PortfolioMatrixOut,
    PortfolioQueryIn,
)
from app.services.portfolio import get_portfolio_matrix, query_portfolio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/matrix", response_model=PortfolioMatrixOut)
def get_matrix(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PortfolioMatrixOut:
    return get_portfolio_matrix(db, user.id)


@router.post("/query", response_model=PortfolioAnswerOut)
def run_portfolio_query(
    body: PortfolioQueryIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PortfolioAnswerOut:
    return query_portfolio(db, user.id, body.question, body.document_ids)
