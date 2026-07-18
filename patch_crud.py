import re

def main():
    with open('gateway/app/routes/crud.py', 'r') as f:
        content = f.read()

    # 1. Fix get_students
    # Find:
    #         if profile:
    #             grade = profile.grade
    
    # We need to fetch teacher and parent user_ids
    get_students_replacement = """        primary_teacher_id = None
        parent_id = None
        if profile:
            grade = profile.grade
            if profile.primary_teacher_id:
                t_res = await db.execute(select(Teacher).where(Teacher.id == profile.primary_teacher_id))
                t_obj = t_res.scalar_one_or_none()
                if t_obj:
                    primary_teacher_id = t_obj.user_id
            if profile.parent_id:
                p_res_obj = await db.execute(select(Parent).where(Parent.id == profile.parent_id))
                p_obj = p_res_obj.scalar_one_or_none()
                if p_obj:
                    parent_id = p_obj.user_id

        student_list.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "grade": grade,
            "primary_teacher_id": primary_teacher_id,
            "parent_id": parent_id,
            "role_id": u.role_id,
            "created_at": u.created_at,
            "ranking": ranking_obj,
            "test_results": test_results_obj,
        })"""
    
    content = re.sub(
        r'        if profile:\s+grade = profile\.grade\s+student_list\.append\(\{\s+"id": u\.id,\s+"name": u\.name,\s+"email": u\.email,\s+"grade": grade,\s+"role_id": u\.role_id,\s+"created_at": u\.created_at,\s+"ranking": ranking_obj,\s+"test_results": test_results_obj,\s+\}\)',
        get_students_replacement,
        content
    )

    # 2. Fix get_student and create_student / update_student returns
    # They return profile.primary_teacher_id. We need a helper or just replace them.
    # Actually, the simplest approach for create/update/get is to write a small helper:
    # Wait, the returns are simple dicts. Let's just modify the endpoints using regex.

    # 3. Fix create_student payload mapping
    create_payload_pattern = r'db_profile = Student\(\s+user_id=db_user\.id,\s+grade=student\.grade,\s+years_studying_english=student\.years_studying_english,\s+learning_environment=student\.learning_environment,\s+self_assessment_level=student\.self_assessment_level,\s+learning_goal=student\.learning_goal,\s+primary_teacher_id=student\.primary_teacher_id,\s+parent_id=student\.parent_id\s+\)'

    create_replacement = """
    t_id = None
    if student.primary_teacher_id:
        t_res = await db.execute(select(Teacher).where(Teacher.user_id == student.primary_teacher_id))
        t_obj = t_res.scalar_one_or_none()
        if t_obj:
            t_id = t_obj.id

    p_id = None
    if student.parent_id:
        p_res_obj = await db.execute(select(Parent).where(Parent.user_id == student.parent_id))
        p_obj = p_res_obj.scalar_one_or_none()
        if p_obj:
            p_id = p_obj.id

    db_profile = Student(
        user_id=db_user.id,
        grade=student.grade,
        years_studying_english=student.years_studying_english,
        learning_environment=student.learning_environment,
        self_assessment_level=student.self_assessment_level,
        learning_goal=student.learning_goal,
        primary_teacher_id=t_id,
        parent_id=p_id
    )
"""
    content = re.sub(create_payload_pattern, create_replacement, content)

    # 4. Fix update_student
    update_payload_pattern = r'        if "primary_teacher_id" in update_data:\s+profile\.primary_teacher_id = update_data\["primary_teacher_id"\]\s+if "parent_id" in update_data:\s+profile\.parent_id = update_data\["parent_id"\]'
    
    update_replacement = """        if "primary_teacher_id" in update_data:
            if update_data["primary_teacher_id"] is not None:
                t_res = await db.execute(select(Teacher).where(Teacher.user_id == update_data["primary_teacher_id"]))
                t_obj = t_res.scalar_one_or_none()
                profile.primary_teacher_id = t_obj.id if t_obj else None
            else:
                profile.primary_teacher_id = None
        if "parent_id" in update_data:
            if update_data["parent_id"] is not None:
                p_res_obj = await db.execute(select(Parent).where(Parent.user_id == update_data["parent_id"]))
                p_obj = p_res_obj.scalar_one_or_none()
                profile.parent_id = p_obj.id if p_obj else None
            else:
                profile.parent_id = None"""

    content = re.sub(update_payload_pattern, update_replacement, content)

    # 5. Fix the profile returns for get_student, create_student, update_student
    # We replace `"primary_teacher_id": profile.primary_teacher_id if profile else None,`
    # Wait, we need to look it up!
    # Instead of looking it up in every return, we can just look it up.
    # Actually, since these endpoints return `StudentResponse`, and we need `primary_teacher_id` as `user_id`.
    # Let's replace the whole return block for get_student
    
    with open('gateway/app/routes/crud_patched.py', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    main()
