-- SQLite Schema for MAS Group Formation System

-- Table 1: Students
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_number TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    gwa REAL CHECK (gwa >= 1.00 AND gwa <= 5.00),
    year_level INTEGER CHECK (year_level BETWEEN 1 AND 5),
    program TEXT DEFAULT 'Computer Science',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Technical Skills
CREATE TABLE IF NOT EXISTS technical_skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    proficiency_level TEXT CHECK(proficiency_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')) NOT NULL,
    years_experience REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 3: Personality Traits (Big Five)
CREATE TABLE IF NOT EXISTS personality_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    openness INTEGER CHECK (openness BETWEEN 1 AND 5),
    conscientiousness INTEGER CHECK (conscientiousness BETWEEN 1 AND 5),
    extraversion INTEGER CHECK (extraversion BETWEEN 1 AND 5),
    agreeableness INTEGER CHECK (agreeableness BETWEEN 1 AND 5),
    neuroticism INTEGER CHECK (neuroticism BETWEEN 1 AND 5),
    learning_style TEXT CHECK(learning_style IN ('Visual', 'Auditory', 'Reading/Writing', 'Kinesthetic')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 4: Schedule Availability
CREATE TABLE IF NOT EXISTS availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')) NOT NULL,
    time_slot TEXT NOT NULL,
    is_available INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 5: Groups
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    project_title TEXT,
    compatibility_score REAL,
    formation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('Active', 'Completed', 'Disbanded')) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 6: Group Members
CREATE TABLE IF NOT EXISTS group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    role TEXT CHECK(role IN ('Leader', 'Member', 'Coordinator')) DEFAULT 'Member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE (student_id, group_id)
);

-- Table 7: Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    description TEXT,
    required_skills TEXT,
    complexity_level TEXT CHECK(complexity_level IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
    estimated_hours REAL,
    deadline DATE,
    status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed', 'Overdue')) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

-- Table 8: Task Assignments
CREATE TABLE IF NOT EXISTS task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage BETWEEN 0 AND 100),
    actual_hours REAL DEFAULT 0,
    status TEXT CHECK(status IN ('Assigned', 'In Progress', 'Completed', 'Needs Help')) DEFAULT 'Assigned',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Table 9: System Logs (for compliance tracking)
CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    user_type TEXT CHECK(user_type IN ('Student', 'Faculty', 'System')) NOT NULL,
    user_id INTEGER,
    description TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_student_number ON students(student_number);
CREATE INDEX IF NOT EXISTS idx_student_email ON students(email);
CREATE INDEX IF NOT EXISTS idx_skills_student ON technical_skills(student_id);
CREATE INDEX IF NOT EXISTS idx_availability_student ON availability(student_id);
CREATE INDEX IF NOT EXISTS idx_group_members_student ON group_members(student_id);
CREATE INDEX IF NOT EXISTS idx_group_members_group ON group_members(group_id);
CREATE INDEX IF NOT EXISTS idx_tasks_group ON tasks(group_id);
CREATE INDEX IF NOT EXISTS idx_task_assignments_task ON task_assignments(task_id);