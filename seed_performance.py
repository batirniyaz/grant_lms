
import asyncio
import random
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.db import async_session_maker
from auth.model import User, Student, Mentor, MonthlyScore, Certificate, CertificateStatus, UserRole
from backend.models.group_model import Group
from auth.util import get_password_hash
from grant_config import CERT_POINTS
import datetime

async def seed_performance_data():
    async with async_session_maker() as session:
        print("🚀 Starting the 'Shine' Seeding Performance Script...")
        
        # 1. Fetch all students with their groups and mentors
        result = await session.execute(
            select(Student).options(
                selectinload(Student.user),
                selectinload(Student.group).selectinload(Group.mentor)
            )
        )
        students = result.scalars().all()
        print(f"Found {len(students)} students.")

        if not students:
            print("❌ No students found in DB. Please run your initial faker scripts first.")
            return

        months = [3, 4, 5] # March, April, May
        year = 2026
        
        cert_types = list(CERT_POINTS.keys())

        for student in students:
            # Randomly decide student profile: "Excellent", "Average", "Risk", "Failing"
            profile = random.choices(
                ["excellent", "average", "risk", "failing"], 
                weights=[20, 50, 20, 10]
            )[0]

            # Generate monthly scores
            for month in months:
                if profile == "excellent":
                    acad = random.uniform(90, 100)
                    att = random.uniform(95, 100)
                    ass = random.uniform(90, 100)
                    disc = random.uniform(90, 100)
                    tutor = random.uniform(4.5, 5.0)
                elif profile == "average":
                    acad = random.uniform(82, 92)
                    att = random.uniform(85, 95)
                    ass = random.uniform(75, 90)
                    disc = random.uniform(80, 100)
                    tutor = random.uniform(3.5, 4.5)
                elif profile == "risk":
                    acad = random.uniform(78, 85) # Might fall below 80
                    att = random.uniform(75, 85)
                    ass = random.uniform(70, 80)
                    disc = random.uniform(70, 85)
                    tutor = random.uniform(3.0, 4.0)
                else: # failing
                    acad = random.uniform(60, 79)
                    att = random.uniform(60, 80)
                    ass = random.uniform(50, 70)
                    disc = random.uniform(50, 80)
                    tutor = random.uniform(1.0, 3.0)

                # Penalties and bonuses (randomly occurring)
                penalty = -2.0 if random.random() < 0.2 else 0.0
                employment = random.choice([0.0, 5.0, 7.0, 10.0]) if profile in ["excellent", "average"] and random.random() < 0.3 else 0.0
                recovery = 2.0 if penalty < 0 and random.random() < 0.5 else 0.0

                # Check if student has mentor to give tutor score
                # If no mentor, tutor score remains 0.0 as per logic
                final_tutor = tutor if student.group and student.group.mentor else 0.0

                m_score = MonthlyScore(
                    student_id=student.user_id,
                    month=month,
                    year=year,
                    academic_percent=round(acad, 2),
                    attendance_percent=round(att, 2),
                    assignment_score=round(ass, 2),
                    discipline_score=round(disc, 2),
                    tutor_score=round(final_tutor, 2),
                    penalty_score=penalty,
                    recovery_score=recovery,
                    employment_score=employment
                )
                session.add(m_score)

            # 2. Generate Certificates
            num_certs = random.randint(0, 3)
            for i in range(num_certs):
                ctype = random.choice(cert_types)
                status = random.choice([CertificateStatus.APPROVED, CertificateStatus.PENDING, CertificateStatus.REJECTED])
                points = CERT_POINTS[ctype] if status == CertificateStatus.APPROVED else 0.0
                
                cert = Certificate(
                    student_id=student.user_id,
                    title=f"Cert for {ctype} #{i+1}",
                    cert_type=ctype,
                    file_path=f"uploads/certificates/fake_cert_{student.user_id}_{i}.pdf",
                    status=status,
                    points=points
                )
                session.add(cert)

        print("💾 Saving all performance data to DB...")
        await session.commit()
        print("✨ Success! DB populated with complex performance data.")
        print("📊 March, April, May scores generated for all students.")
        print("🏆 Leaderboard is now ready for your best performance!")

if __name__ == "__main__":
    asyncio.run(seed_performance_data())
