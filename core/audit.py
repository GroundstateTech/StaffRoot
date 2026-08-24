from sqlalchemy.orm import Session
from db.models import AuditLog, User

def log_event(db: Session, user: User | None, action: str, details: str = "") -> None:
    try:
        row = AuditLog(
            user_id=user.id if user else None,
            action=(action or "UNKNOWN")[:128],
            details=(details or "")[:2000],
        )
        db.add(row)
        db.commit()
    except Exception:
        db.rollback()
