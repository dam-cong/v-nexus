-- V-Nexus Database Schema

-- 1. Roles table
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);

-- Pre-populate default roles
INSERT INTO roles (id, name, description)
VALUES 
    (1, 'hoc_sinh', 'Học sinh tham gia học tập'),
    (2, 'giao_vien', 'Giáo viên quản lý và giảng dạy'),
    (3, 'admin', 'Quản trị viên hệ thống')
ON CONFLICT (id) DO NOTHING;

-- 2. Teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role_id INT REFERENCES roles(id) DEFAULT 2,
    subject VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Students table
CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role_id INT REFERENCES roles(id) DEFAULT 1,
    grade VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Rankings table (Xếp hạng)
CREATE TABLE IF NOT EXISTS rankings (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    score INT DEFAULT 0,
    level VARCHAR(50) DEFAULT 'Beginner',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Survey Evaluations table (Khảo sát đầu vào)
CREATE TABLE IF NOT EXISTS survey_evaluations (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    years_studying_english INT DEFAULT 0,
    learning_environment VARCHAR(100), -- 'school', 'center', 'self_study'
    self_assessment_level VARCHAR(50), -- 'A1', 'A2', 'B1', 'B2', etc.
    learning_goal TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
