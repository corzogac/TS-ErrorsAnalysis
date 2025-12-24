# ---------------------------------------------------------------------------
# File    : api/stats.py
# Purpose : Statistics calculation and retrieval functions
# License : MIT
# ---------------------------------------------------------------------------
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .database import AnalysisRecord, UserSession, SystemStats

def log_analysis(
    db: Session,
    metrics: Dict[str, Any],
    n_points: int,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    analysis_name: Optional[str] = None,
    notes: Optional[str] = None
) -> AnalysisRecord:
    """Log an analysis to the database"""

    record = AnalysisRecord(
        session_id=session_id,
        user_id=user_id,
        n_points=n_points,
        rmse=metrics.get("RMSE"),
        nsc=metrics.get("NSC"),
        correlation=metrics.get("Cor"),
        kge2009=metrics.get("KGE2009"),
        metrics_json=metrics,
        analysis_name=analysis_name,
        notes=notes
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    # Update session stats
    if session_id:
        session = db.query(UserSession).filter(UserSession.session_id == session_id).first()
        if session:
            session.analysis_count += 1
            session.last_active = datetime.utcnow()
            db.commit()

    return record

def get_or_create_session(db: Session, session_id: str, user_id: Optional[str] = None) -> UserSession:
    """Get existing session or create new one"""
    session = db.query(UserSession).filter(UserSession.session_id == session_id).first()

    if not session:
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            analysis_count=0
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    else:
        session.last_active = datetime.utcnow()
        if user_id and not session.user_id:
            session.user_id = user_id
        db.commit()

    return session

def get_user_stats(db: Session, user_id: str) -> Dict[str, Any]:
    """Get statistics for a specific user"""

    # Total analyses
    total_analyses = db.query(func.count(AnalysisRecord.id))\
        .filter(AnalysisRecord.user_id == user_id)\
        .scalar() or 0

    # Recent analyses (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_analyses = db.query(func.count(AnalysisRecord.id))\
        .filter(AnalysisRecord.user_id == user_id)\
        .filter(AnalysisRecord.timestamp >= thirty_days_ago)\
        .scalar() or 0

    # Average metrics
    avg_metrics = db.query(
        func.avg(AnalysisRecord.rmse).label("avg_rmse"),
        func.avg(AnalysisRecord.nsc).label("avg_nsc"),
        func.avg(AnalysisRecord.correlation).label("avg_cor"),
        func.avg(AnalysisRecord.kge2009).label("avg_kge")
    ).filter(AnalysisRecord.user_id == user_id).first()

    # Recent analyses
    recent = db.query(AnalysisRecord)\
        .filter(AnalysisRecord.user_id == user_id)\
        .order_by(desc(AnalysisRecord.timestamp))\
        .limit(10)\
        .all()

    return {
        "user_id": user_id,
        "total_analyses": total_analyses,
        "recent_analyses_30d": recent_analyses,
        "average_metrics": {
            "rmse": float(avg_metrics.avg_rmse) if avg_metrics.avg_rmse else None,
            "nsc": float(avg_metrics.avg_nsc) if avg_metrics.avg_nsc else None,
            "correlation": float(avg_metrics.avg_cor) if avg_metrics.avg_cor else None,
            "kge2009": float(avg_metrics.avg_kge) if avg_metrics.avg_kge else None
        },
        "recent_analyses": [
            {
                "id": r.id,
                "timestamp": r.timestamp.isoformat(),
                "n_points": r.n_points,
                "rmse": r.rmse,
                "nsc": r.nsc,
                "name": r.analysis_name
            } for r in recent
        ]
    }

def get_system_stats(db: Session) -> Dict[str, Any]:
    """Get overall system statistics"""

    # Total counts
    total_analyses = db.query(func.count(AnalysisRecord.id)).scalar() or 0
    total_sessions = db.query(func.count(UserSession.id)).scalar() or 0
    unique_users = db.query(func.count(func.distinct(AnalysisRecord.user_id)))\
        .filter(AnalysisRecord.user_id.isnot(None))\
        .scalar() or 0

    # Last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    analyses_24h = db.query(func.count(AnalysisRecord.id))\
        .filter(AnalysisRecord.timestamp >= yesterday)\
        .scalar() or 0

    # Average metrics across all analyses
    avg_metrics = db.query(
        func.avg(AnalysisRecord.rmse).label("avg_rmse"),
        func.avg(AnalysisRecord.nsc).label("avg_nsc"),
        func.avg(AnalysisRecord.correlation).label("avg_cor"),
        func.avg(AnalysisRecord.kge2009).label("avg_kge")
    ).first()

    # Most active users
    top_users = db.query(
        AnalysisRecord.user_id,
        func.count(AnalysisRecord.id).label("count")
    ).filter(AnalysisRecord.user_id.isnot(None))\
     .group_by(AnalysisRecord.user_id)\
     .order_by(desc("count"))\
     .limit(5)\
     .all()

    return {
        "total_analyses": total_analyses,
        "total_sessions": total_sessions,
        "unique_users": unique_users,
        "analyses_last_24h": analyses_24h,
        "average_metrics": {
            "rmse": float(avg_metrics.avg_rmse) if avg_metrics.avg_rmse else None,
            "nsc": float(avg_metrics.avg_nsc) if avg_metrics.avg_nsc else None,
            "correlation": float(avg_metrics.avg_cor) if avg_metrics.avg_cor else None,
            "kge2009": float(avg_metrics.avg_kge) if avg_metrics.avg_kge else None
        },
        "top_users": [
            {"user_id": u[0], "analysis_count": u[1]} for u in top_users
        ]
    }

def get_analysis_history(
    db: Session,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get analysis history"""

    query = db.query(AnalysisRecord)

    if user_id:
        query = query.filter(AnalysisRecord.user_id == user_id)
    if session_id:
        query = query.filter(AnalysisRecord.session_id == session_id)

    records = query.order_by(desc(AnalysisRecord.timestamp)).limit(limit).all()

    return [
        {
            "id": r.id,
            "timestamp": r.timestamp.isoformat(),
            "n_points": r.n_points,
            "rmse": r.rmse,
            "nsc": r.nsc,
            "correlation": r.correlation,
            "kge2009": r.kge2009,
            "name": r.analysis_name,
            "metrics": r.metrics_json
        } for r in records
    ]
