import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gateway.app.routes.crud import select_alternative_path, SelectAlternativePathSubmit
from db.models import StudentTestResult

@pytest.mark.asyncio
async def test_select_alternative_path_unauthorized():
    db = AsyncMock()
    body = SelectAlternativePathSubmit(path_key="path_1_back_to_roots")
    user = {"role": "hoc_sinh", "id": 1}  # Học sinh không có quyền chọn lộ trình

    with pytest.raises(HTTPException) as exc_info:
        await select_alternative_path(result_id=999, body=body, db=db, user=user)
    
    assert exc_info.value.status_code == 403
    assert "Chỉ giáo viên hoặc quản trị viên" in exc_info.value.detail

@pytest.mark.asyncio
async def test_select_alternative_path_not_found():
    db = AsyncMock()
    
    # Mock kết quả truy vấn db.execute
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    
    body = SelectAlternativePathSubmit(path_key="path_1_back_to_roots")
    user = {"role": "giao_vien", "id": 2}  # Giáo viên hợp lệ

    with pytest.raises(HTTPException) as exc_info:
        await select_alternative_path(result_id=999, body=body, db=db, user=user)
    
    assert exc_info.value.status_code == 404
    assert "Test result not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_select_alternative_path_success():
    db = AsyncMock()
    
    test_result = StudentTestResult(
        id=123,
        user_id=1,
        test_id=1,
        alternative_plans={
            "alternative_paths": {
                "path_1_back_to_roots": {
                    "reasoning_cot": "Cần củng cố gốc rễ",
                    "primary_difference": "Quay lại ôn tập hằng đẳng thức đáng nhớ",
                    "target_prerequisite_skills": ["as3.u5.l3"],
                    "action_steps": [
                        {
                            "step_number": 1,
                            "skill_id": "as3.u5.l3",
                            "action_description": "Ôn tập hằng đẳng thức số 1 và số 2.",
                            "estimated_duration_mins": 20
                        }
                    ],
                    "expected_outcome": "Thành thạo hằng đẳng thức"
                }
            }
        }
    )
    
    # Mock kết quả truy vấn db.execute trả về test_result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_result
    db.execute.return_value = mock_result
    
    body = SelectAlternativePathSubmit(path_key="path_1_back_to_roots")
    user = {"role": "giao_vien", "id": 2}

    res = await select_alternative_path(result_id=123, body=body, db=db, user=user)
    
    assert res == test_result
    assert res.training_plan is not None
    
    # Kiểm tra tính chính xác của dữ liệu format thành training_plan
    import json
    plan_data = json.loads(res.training_plan)
    assert "path_1_back_to_roots" in plan_data["summary"]
    assert "Cần củng cố gốc rễ" in plan_data["summary"]
    assert len(plan_data["steps"]) == 1
    assert plan_data["steps"][0]["step_order"] == 1
    assert plan_data["steps"][0]["practice_tip"] == "Ôn tập hằng đẳng thức số 1 và số 2."
    assert "Thành thạo hằng đẳng thức" in plan_data["closing"]
