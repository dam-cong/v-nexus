"""SQLAlchemy ORM Models representing the database schema."""
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer, String, Text, Boolean, ForeignKey, JSON, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChatLog(Base):
    __tablename__ = "chat_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_message: Mapped[str] = mapped_column(Text)
    agent_reply: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users")
    student_profile: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", cascade="all, delete-orphan")
    teacher_profile: Mapped[Optional["Teacher"]] = relationship("Teacher", back_populates="user", cascade="all, delete-orphan")
    parent_profile: Mapped[Optional["Parent"]] = relationship("Parent", back_populates="user", cascade="all, delete-orphan")
    ranking: Mapped[Optional["Ranking"]] = relationship("Ranking", back_populates="user", cascade="all, delete-orphan")
    test_results: Mapped[list["StudentTestResult"]] = relationship("StudentTestResult", back_populates="user", cascade="all, delete-orphan")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    subject: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="teacher_profile")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="primary_teacher")
    evaluations: Mapped[list["TeacherEvaluation"]] = relationship("TeacherEvaluation", back_populates="teacher")

class Parent(Base):
    __tablename__ = "parents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="parent_profile")
    students: Mapped[list["Student"]] = relationship("Student", back_populates="parent")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    years_studying_english: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    learning_environment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    self_assessment_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    learning_goal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    training_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_teacher_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="student_profile")
    primary_teacher: Mapped[Optional["Teacher"]] = relationship("Teacher", back_populates="students")
    parent: Mapped[Optional["Parent"]] = relationship("Parent", back_populates="students")
    evaluations: Mapped[list["TeacherEvaluation"]] = relationship("TeacherEvaluation", back_populates="student", cascade="all, delete-orphan")


class Ranking(Base):
    __tablename__ = "rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[str] = mapped_column(String(50), default="Beginner")
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="ranking")


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("question_id", name="uq_question_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    question_id: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    instruction_label: Mapped[str] = mapped_column(String(50), nullable=False)
    skill_id: Mapped[str] = mapped_column(String(50), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(200), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False)
    prompt: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    correct_option_id: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    placement_links: Mapped[list["PlacementTestQuestion"]] = relationship("PlacementTestQuestion", back_populates="question")


class PlacementTest(Base):
    __tablename__ = "placement_tests"
    __table_args__ = (UniqueConstraint("test_id", name="uq_placement_test_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    mascot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    steps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    levels: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    adaptive_config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    question_links: Mapped[list["PlacementTestQuestion"]] = relationship("PlacementTestQuestion", back_populates="test")
    test_results: Mapped[list["StudentTestResult"]] = relationship("StudentTestResult", back_populates="test")


class PlacementTestQuestion(Base):
    __tablename__ = "placement_test_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("placement_tests.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    test: Mapped["PlacementTest"] = relationship("PlacementTest", back_populates="question_links")
    question: Mapped["Question"] = relationship("Question", back_populates="placement_links")


class StudentTestResult(Base):
    __tablename__ = "student_test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    test_id: Mapped[int] = mapped_column(Integer, ForeignKey("placement_tests.id"), nullable=False)
    answers: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    max_score: Mapped[int] = mapped_column(Integer, default=0)
    percentage: Mapped[float] = mapped_column(Integer, default=0)
    result_level: Mapped[str] = mapped_column(String(50), nullable=False)
    cefr: Mapped[str] = mapped_column(String(10), nullable=False)
    time_total_sec: Mapped[int] = mapped_column(Integer, default=0)
    mastery: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    gaps: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    training_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    alternative_plans: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_roadmap_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    roadmap_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    quick_check_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    test_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="test_results")
    test: Mapped["PlacementTest"] = relationship("PlacementTest", back_populates="test_results")

class TeacherEvaluation(Base):
    __tablename__ = "teacher_evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="evaluations")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="evaluations")


class AppSetting(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
