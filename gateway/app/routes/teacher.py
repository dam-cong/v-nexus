"""Dashboard giáo viên — teacher_id lấy từ token, kiểm tra sở hữu lớp trước khi trả dữ liệu."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from db.connector import get_session
from db.models import ClassRoom, Teacher, User, UserRole
from domain.dashboard_queries import teacher_dashboard_query
from domain.knowledge_graph import load_knowledge_graph

from ..auth import require_role

router = APIRouter(prefix="/teacher", tags=["teacher"])
_graph = load_knowledge_graph()


@router.get("/dashboard/{class_id}")
async def get_teacher_dashboard(
    class_id: int,
    session=Depends(get_session),
    user: User = Depends(require_role(UserRole.teacher)),
):
    teacher = (
        await session.execute(select(Teacher).where(Teacher.user_id == user.id))
    ).scalar_one_or_none()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ giáo viên cho tài khoản này.")

    classroom = (
        await session.execute(select(ClassRoom).where(ClassRoom.id == class_id))
    ).scalar_one_or_none()
    if classroom is None or classroom.teacher_id != teacher.id:
        raise HTTPException(status_code=403, detail="Bạn không phụ trách lớp này.")

    return await teacher_dashboard_query(session, class_id, _graph)
