"""Dashboard phụ huynh — parent_id lấy từ token (KHÔNG nhận qua query param), tránh
việc chỉ tin input từ client cho dữ liệu nhạy cảm của con."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from db.connector import get_session
from db.models import Parent, User, UserRole
from domain.dashboard_queries import parent_dashboard_query
from domain.knowledge_graph import load_knowledge_graph

from ..auth import require_role

router = APIRouter(prefix="/parent", tags=["parent"])
_graph = load_knowledge_graph()


@router.get("/dashboard/{student_id}")
async def get_parent_dashboard(
    student_id: int,
    session=Depends(get_session),
    user: User = Depends(require_role(UserRole.parent)),
):
    parent = (
        await session.execute(select(Parent).where(Parent.user_id == user.id))
    ).scalar_one_or_none()
    if parent is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ phụ huynh cho tài khoản này.")

    result = await parent_dashboard_query(session, student_id, parent.id, _graph)
    if result.get("error") == "access_denied":
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem dữ liệu học sinh này.")
    return result
