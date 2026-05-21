
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from auth.model import Student, MonthlyScore, Certificate, CertificateStatus
from auth.schema import LeaderboardRow
from grant_config import *

async def calculate_student_kpi(student: Student) -> LeaderboardRow:
    monthly_scores = student.monthly_scores
    certificates = student.certificates
    
    # 1. Monthly averages
    count = len(monthly_scores)
    if count == 0:
        # Default empty row if no data
        return LeaderboardRow(
            student_name=f"{student.user.first_name} {student.user.last_name}",
            group_name=student.group.group_number if student.group else "N/A",
            student_id=student.student_id,
            current_status="Grant" if student.is_grant else "Kontrakt",
            academic_percent=0, academic_ball=0,
            attendance_percent=0, attendance_ball=0,
            assignment_ball=0, activity_ball=0,
            tutor_ball=0, discipline_ball=0,
            total_kpi=0, penalty=0, recovery=0, employment=0,
            final_score=0, next_status=STATUS_CANCELLED_LOW_SCORE, risk="Low Chance"
        )

    avg_academic_pct = sum(m.academic_percent for m in monthly_scores) / count
    avg_attendance_pct = sum(m.attendance_percent for m in monthly_scores) / count
    avg_assignment = sum(m.assignment_score for m in monthly_scores) / count
    avg_discipline = sum(m.discipline_score for m in monthly_scores) / count
    avg_tutor = sum(m.tutor_score for m in monthly_scores) / count
    
    total_penalty = sum(m.penalty_score for m in monthly_scores)
    total_recovery = sum(m.recovery_score for m in monthly_scores)
    total_employment = sum(m.employment_score for m in monthly_scores)
    
    # 2. Activity score (Certificates)
    approved_certs_points = sum(c.points for c in certificates if c.status == CertificateStatus.APPROVED)
    activity_ball = min(approved_certs_points, MAX_ACTIVITY) # Capped at max
    
    # 3. KPI Component calculation (Weighted)
    academic_ball = (avg_academic_pct / 100) * MAX_ACADEMIC
    attendance_ball = (avg_attendance_pct / 100) * MAX_ATTENDANCE
    assignment_ball = (avg_assignment / 100) * MAX_ASSIGNMENT # Assuming assignment_score is 0-100
    discipline_ball = (avg_discipline / 100) * MAX_DISCIPLINE
    tutor_ball = avg_tutor # Tutor score is already 1-5
    
    total_kpi = academic_ball + attendance_ball + assignment_ball + activity_ball + tutor_ball + discipline_ball
    
    # 4. Final adjustments
    # Penalty is subtracted, recovery added, employment bonus added
    final_score = total_kpi + total_penalty + total_recovery + total_employment
    
    # 5. Status determination
    if avg_academic_pct < ACADEMIC_THRESHOLD_PERCENT:
        next_status = STATUS_CANCELLED_ACADEMIC
    elif final_score >= GRANT_CONTINUE_THRESHOLD:
        next_status = STATUS_GRANT_CONTINUES
    elif final_score >= PROBATION_THRESHOLD:
        next_status = STATUS_PROBATION
    else:
        next_status = STATUS_CANCELLED_LOW_SCORE
        
    # Risk assessment (Chance logic)
    if avg_academic_pct < ACADEMIC_THRESHOLD_PERCENT or final_score < 80:
        risk = "Low Chance"
    elif final_score > 90:
        risk = "High Chance"
    else:
        risk = "Medium Chance"

    return LeaderboardRow(
        student_name=f"{student.user.first_name} {student.user.last_name}",
        group_name=student.group.group_number if student.group else "N/A",
        student_id=student.student_id,
        current_status="Grant" if student.is_grant else "Kontrakt",
        academic_percent=avg_academic_pct,
        academic_ball=round(academic_ball, 2),
        attendance_percent=avg_attendance_pct,
        attendance_ball=round(attendance_ball, 2),
        assignment_ball=round(assignment_ball, 2),
        activity_ball=round(activity_ball, 2),
        tutor_ball=round(tutor_ball, 2),
        discipline_ball=round(discipline_ball, 2),
        total_kpi=round(total_kpi, 2),
        penalty=round(total_penalty, 2),
        recovery=round(total_recovery, 2),
        employment=round(total_employment, 2),
        final_score=round(final_score, 2),
        next_status=next_status,
        risk=risk
    )

async def get_leaderboard_data(db: AsyncSession, limit: int = None, page: int = 1) -> List[LeaderboardRow]:
    result = await db.execute(
        select(Student)
        .options(
            selectinload(Student.user),
            selectinload(Student.group),
            selectinload(Student.monthly_scores),
            selectinload(Student.certificates)
        )
    )
    students = result.scalars().all()
    
    leaderboard = []
    for student in students:
        row = await calculate_student_kpi(student)
        leaderboard.append(row)
        
    # Sort by final score descending
    leaderboard.sort(key=lambda x: x.final_score, reverse=True)
    
    # Manual pagination after calculation
    if limit:
        start = (page - 1) * limit
        end = start + limit
        return leaderboard[start:end]
        
    return leaderboard
