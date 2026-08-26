from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ForwardingRule
from app.schemas import RuleCreate, RuleUpdate, RuleResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.get("/", response_model=list[RuleResponse])
def list_rules(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rules = (
        db.query(ForwardingRule)
        .filter(ForwardingRule.user_id == user.id)
        .order_by(ForwardingRule.priority.desc())
        .all()
    )
    return [RuleResponse.model_validate(r) for r in rules]


@router.post("/", response_model=RuleResponse)
def create_rule(
    data: RuleCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = ForwardingRule(user_id=user.id, **data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return RuleResponse.model_validate(rule)


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: str,
    data: RuleUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = db.query(ForwardingRule).filter(ForwardingRule.id == rule_id, ForwardingRule.user_id == user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(rule, k, v)
    db.commit()
    db.refresh(rule)
    return RuleResponse.model_validate(rule)


@router.delete("/{rule_id}")
def delete_rule(
    rule_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = db.query(ForwardingRule).filter(ForwardingRule.id == rule_id, ForwardingRule.user_id == user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"ok": True}
