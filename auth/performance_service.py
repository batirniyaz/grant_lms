
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from typing import List

from auth.model import MonthlyScore, Student, Certificate, CertificateStatus
from auth.schema import MonthlyScoreCreate, MonthlyScoreRead, MonthlyScoreUpdate, CertificateRead, CertificateUpdateStatus
from backend.models.group_model import Group
from backend.ws_manager import manager

async def broadcast_leaderboard_update(db: AsyncSession):
    """Recalculates leaderboard and broadcasts to all connected WS clients."""
    try:
        from auth.kpi_service import get_leaderboard_data
        data = await get_leaderboard_data(db)
        data_json = [row.model_dump(mode='json') for row in data]
        await manager.broadcast({"type": "update", "data": data_json})
    except Exception as e:
        # Log error but don't fail the request
        print(f"WebSocket Broadcast Error: {e}")

async def get_monthly_score(db: AsyncSession, student_id: int, month: int, year: int) -> MonthlyScore:
    res = await db.execute(
        select(MonthlyScore).filter_by(student_id=student_id, month=month, year=year)
    )
    return res.scalars().first()

async def upsert_monthly_score_admin(db: AsyncSession, score_in: MonthlyScoreCreate) -> MonthlyScoreRead:
    score = await get_monthly_score(db, score_in.student_id, score_in.month, score_in.year)
    if not score:
        score = MonthlyScore(**score_in.model_dump())
        db.add(score)
    else:
        for k, v in score_in.model_dump(exclude_unset=True).items():
            setattr(score, k, v)
    
    try:
        await db.commit()
        await db.refresh(score)
        await broadcast_leaderboard_update(db)
        return MonthlyScoreRead.model_validate(score)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_monthly_score_admin(db: AsyncSession, score_id: int, score_in: MonthlyScoreUpdate) -> MonthlyScoreRead:
    res = await db.execute(select(MonthlyScore).filter_by(id=score_id))
    score = res.scalars().first()
    if not score:
        raise HTTPException(status_code=404, detail="Score record not found")
    
    for k, v in score_in.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(score, k, v)
            
    try:
        await db.commit()
        await db.refresh(score)
        await broadcast_leaderboard_update(db)
        return MonthlyScoreRead.model_validate(score)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_tutor_score(db: AsyncSession, student_id: int, month: int, year: int, tutor_score: float, mentor_id: int) -> MonthlyScoreRead:
    res = await db.execute(select(Student).filter_by(user_id=student_id))
    student = res.scalars().first()
    if not student: raise HTTPException(status_code=404, detail="Student not found")
    
    if student.group_id:
        res = await db.execute(select(Group).filter_by(id=student.group_id, mentor_id=mentor_id))
        if not res.scalars().first():
            raise HTTPException(status_code=403, detail="You are not the mentor of this student's group")
    else:
        raise HTTPException(status_code=400, detail="Student is not assigned to any group")

    score = await get_monthly_score(db, student_id, month, year)
    if not score:
        score = MonthlyScore(student_id=student_id, month=month, year=year, tutor_score=tutor_score)
        db.add(score)
    else:
        score.tutor_score = tutor_score
        
    try:
        await db.commit()
        await db.refresh(score)
        await broadcast_leaderboard_update(db)
        return MonthlyScoreRead.model_validate(score)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def create_certificate(db: AsyncSession, student_id: int, title: str, cert_type: str, file_path: str) -> CertificateRead:
    cert = Certificate(student_id=student_id, title=title, cert_type=cert_type, file_path=file_path)
    db.add(cert)
    try:
        await db.commit()
        await db.refresh(cert)
        # No broadcast here as it's PENDING and doesn't affect KPI yet
        return CertificateRead.model_validate(cert)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def update_certificate_status(db: AsyncSession, cert_id: int, status_in: CertificateUpdateStatus) -> CertificateRead:
    from grant_config import CERT_POINTS
    res = await db.execute(select(Certificate).filter_by(id=cert_id))
    cert = res.scalars().first()
    if not cert: raise HTTPException(status_code=404, detail="Certificate not found")
    
    cert.status = CertificateStatus(status_in.status)
    cert.points = CERT_POINTS.get(cert.cert_type, 1.0) if cert.status == CertificateStatus.APPROVED else 0.0
    
    try:
        await db.commit()
        await db.refresh(cert)
        await broadcast_leaderboard_update(db)
        return CertificateRead.model_validate(cert)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def get_pending_certificates(db: AsyncSession) -> List[CertificateRead]:
    res = await db.execute(select(Certificate).filter_by(status=CertificateStatus.PENDING))
    certs = res.scalars().all()
    return [CertificateRead.model_validate(c) for c in certs]

async def get_student_performance(db: AsyncSession, student_id: int) -> List[MonthlyScoreRead]:
    # 1. Resolve student (could be user_id or business student_id)
    res = await db.execute(
        select(Student).where((Student.user_id == student_id) | (Student.student_id == student_id))
    )
    student = res.scalars().first()
    if not student:
        return []

    # 2. Fetch scores using the resolved user_id
    res = await db.execute(
        select(MonthlyScore)
        .filter_by(student_id=student.user_id)
        .order_by(MonthlyScore.year.desc(), MonthlyScore.month.desc())
    )
    scores = res.scalars().all()
    return [MonthlyScoreRead.model_validate(s) for s in scores]

async def get_student_certificates(db: AsyncSession, student_id: int) -> List[CertificateRead]:
    # Resolve student user_id
    res = await db.execute(select(Student.user_id).where((Student.user_id == student_id) | (Student.student_id == student_id)))
    uid = res.scalars().first()
    if not uid: return []
    
    res = await db.execute(select(Certificate).filter_by(student_id=uid))
    certs = res.scalars().all()
    return [CertificateRead.model_validate(c) for c in certs]
