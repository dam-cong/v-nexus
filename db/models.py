"""Schema DB cho V-Nexus Tutor. Giữ ChatLog (bot hỏi-đáp), thêm schema gia sư thích ứng."""
import enum
import uuid
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ChatLog(Base):
    __tablename__ = "chat_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_message: Mapped[str] = mapped_column(Text)
    agent_reply: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    parent = "parent"
    school_admin = "school_admin"


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Bảng auth (fastapi-users) — id/email/hashed_password/is_active/is_verified có
    sẵn từ SQLAlchemyBaseUserTableUUID, chỉ thêm `role` để phân quyền route."""

    __tablename__ = "user"

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.student)


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name_vi: Mapped[str] = mapped_column(Text)
    name_en: Mapped[str] = mapped_column(Text)
    grade: Mapped[int] = mapped_column(Integer)
    unit: Mapped[str] = mapped_column(String(32))
    skill_type: Mapped[str] = mapped_column(String(32))  # vocab|grammar|listening|speaking|phonics
    p_init: Mapped[float] = mapped_column(Float, default=0.4)
    p_transit: Mapped[float] = mapped_column(Float, default=0.1)
    p_slip: Mapped[float] = mapped_column(Float, default=0.1)
    p_guess: Mapped[float] = mapped_column(Float, default=0.2)


class SkillPrerequisite(Base):
    __tablename__ = "skill_prerequisite"
    __table_args__ = (UniqueConstraint("prerequisite_skill_id", "dependent_skill_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prerequisite_skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))
    dependent_skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))
    weight: Mapped[float] = mapped_column(Float, default=1.0)


class Question(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))
    content: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str] = mapped_column(String(32))  # mcq|fill_blank|listening|dialogue
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text)
    difficulty: Mapped[int] = mapped_column(Integer)  # 1-5
    source: Mapped[str] = mapped_column(String(64), default="ai_generated")  # teacher_digitized|ai_generated


class Teacher(Base):
    __tablename__ = "teacher"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )


class ClassRoom(Base):
    __tablename__ = "class_room"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher.id"))
    grade: Mapped[int] = mapped_column(Integer)


class Parent(Base):
    __tablename__ = "parent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )


class Student(Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text)
    class_id: Mapped[int] = mapped_column(ForeignKey("class_room.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("parent.id"), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )


class StudentResponse(Base):
    """Log tương tác append-only — nguồn cho replay BKT và biểu đồ tiến độ theo thời gian."""

    __tablename__ = "student_response"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))
    is_correct: Mapped[bool] = mapped_column(Boolean)
    session_type: Mapped[str] = mapped_column(String(32))  # diagnostic|practice
    answered_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    p_mastery_before: Mapped[float] = mapped_column(Float)
    p_mastery_after: Mapped[float] = mapped_column(Float)


class StudentSkillMastery(Base):
    """Cache trạng thái hiện tại — đọc nhanh cho dashboard, khác StudentResponse (log)."""

    __tablename__ = "student_skill_mastery"
    __table_args__ = (UniqueConstraint("student_id", "skill_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id"))
    p_mastery: Mapped[float] = mapped_column(Float, default=0.4)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    stuck_since: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
