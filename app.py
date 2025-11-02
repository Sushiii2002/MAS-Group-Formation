from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from utils.db_connection import DatabaseConnection
from agents.matcher_agent_ga import MatcherAgentGA
from agents.coordinator_agent import CoordinatorAgent
from datetime import datetime
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False

# ============================================================
# HTML PAGE ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register')
def register():
    """Student registration page"""
    return render_template('student_registration.html')

@app.route('/faculty')
def faculty():
    """Faculty dashboard page"""
    return render_template('faculty_dashboard.html')

@app.route('/student')
def student():
    """Student dashboard page"""
    return render_template('student_dashboard.html')

@app.route('/groups')
def groups():
    """Groups view page"""
    return render_template('groups_view.html')

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_db():
    """Helper function to get database connection"""
    db = DatabaseConnection()
    db.connect()
    return db

def success_response(data, message="Success", status=200):
    """Standardized success response"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }), status

def error_response(message, status=400):
    """Standardized error response"""
    return jsonify({
        'success': False,
        'message': message,
        'data': None
    }), status

# ============================================================
# STUDENT ENDPOINTS
# ============================================================

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    try:
        db = get_db()
        query = """
        SELECT id, student_number, first_name, last_name, 
               email, gwa, year_level, program, created_at
        FROM students
        ORDER BY last_name, first_name
        """
        students = db.fetch_all(query)
        db.disconnect()
        return success_response(students, f"Found {len(students)} students")
    except Exception as e:
        return error_response(f"Error fetching students: {str(e)}", 500)

@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    """Get single student with complete profile"""
    try:
        db = get_db()
        student_query = """
        SELECT id, student_number, first_name, last_name, 
               email, gwa, year_level, program, created_at
        FROM students WHERE id = ?
        """
        student = db.fetch_one(student_query, (student_id,))
        
        if not student:
            db.disconnect()
            return error_response("Student not found", 404)
        
        skills_query = """
        SELECT skill_name, proficiency_level, years_experience
        FROM technical_skills WHERE student_id = ?
        """
        student['skills'] = db.fetch_all(skills_query, (student_id,))
        
        traits_query = """
        SELECT openness, conscientiousness, extraversion,
               agreeableness, neuroticism, learning_style
        FROM personality_traits WHERE student_id = ?
        """
        student['traits'] = db.fetch_one(traits_query, (student_id,))
        
        avail_query = """
        SELECT day_of_week, time_slot, is_available
        FROM availability WHERE student_id = ?
        """
        student['availability'] = db.fetch_all(avail_query, (student_id,))
        
        db.disconnect()
        return success_response(student, "Student profile retrieved")
    except Exception as e:
        return error_response(f"Error fetching student: {str(e)}", 500)

@app.route('/api/students', methods=['POST'])
def create_student():
    """Create new student"""
    try:
        data = request.get_json()
        required = ['student_number', 'first_name', 'last_name', 'email', 'gwa', 'year_level']
        for field in required:
            if field not in data:
                return error_response(f"Missing required field: {field}")
        
        db = get_db()
        check_query = "SELECT id FROM students WHERE student_number = ?"
        existing = db.fetch_one(check_query, (data['student_number'],))
        
        if existing:
            db.disconnect()
            return error_response("Student number already exists", 409)
        
        insert_query = """
        INSERT INTO students 
        (student_number, first_name, last_name, email, gwa, year_level, program)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        student_id = db.insert_and_get_id(
            insert_query,
            (data['student_number'], data['first_name'], data['last_name'],
             data['email'], data['gwa'], data['year_level'], 
             data.get('program', 'Computer Science'))
        )
        db.disconnect()
        
        if student_id:
            return success_response({'id': student_id}, "Student created successfully", 201)
        else:
            return error_response("Failed to create student", 500)
    except Exception as e:
        return error_response(f"Error creating student: {str(e)}", 500)

@app.route('/api/students/<int:student_id>/skills', methods=['POST'])
def add_student_skills(student_id):
    """Add skills to a student"""
    try:
        data = request.get_json()
        if 'skills' not in data or not isinstance(data['skills'], list):
            return error_response("Invalid request: 'skills' array required")
        
        db = get_db()
        check_query = "SELECT id FROM students WHERE id = ?"
        if not db.fetch_one(check_query, (student_id,)):
            db.disconnect()
            return error_response("Student not found", 404)
        
        insert_query = """
        INSERT INTO technical_skills 
        (student_id, skill_name, proficiency_level, years_experience)
        VALUES (?, ?, ?, ?)
        """
        added_count = 0
        for skill in data['skills']:
            if db.execute_query(
                insert_query,
                (student_id, skill['skill_name'], 
                 skill['proficiency_level'], 
                 skill.get('years_experience', 0))
            ):
                added_count += 1
        
        db.disconnect()
        return success_response({'added_count': added_count}, f"Added {added_count} skills")
    except Exception as e:
        return error_response(f"Error adding skills: {str(e)}", 500)

# ============================================================
# GROUP ENDPOINTS
# ============================================================

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all groups with their members"""
    try:
        db = get_db()
        groups_query = """
        SELECT id, group_name, project_title, compatibility_score,
               formation_date, status
        FROM groups ORDER BY formation_date DESC
        """
        groups = db.fetch_all(groups_query)
        
        for group in groups:
            members_query = """
            SELECT s.id, s.first_name, s.last_name, s.gwa,
                   gm.role, gm.joined_at
            FROM students s
            JOIN group_members gm ON s.id = gm.student_id
            WHERE gm.group_id = ?
            ORDER BY gm.role DESC, s.last_name
            """
            group['members'] = db.fetch_all(members_query, (group['id'],))
            group['member_count'] = len(group['members'])
        
        db.disconnect()
        return success_response(groups, f"Found {len(groups)} groups")
    except Exception as e:
        return error_response(f"Error fetching groups: {str(e)}", 500)

@app.route('/api/groups/clear', methods=['DELETE'])
def clear_all_groups():
    """Clear all groups and related data"""
    try:
        db = get_db()
        
        # Delete in correct order (foreign key constraints)
        db.execute_query("DELETE FROM task_assignments")
        db.execute_query("DELETE FROM tasks")
        db.execute_query("DELETE FROM group_members")
        db.execute_query("DELETE FROM groups")
        
        db.disconnect()
        
        return success_response(None, "All groups cleared successfully")
    except Exception as e:
        return error_response(f"Error clearing groups: {str(e)}", 500)

@app.route('/api/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    """Get single group with complete details"""
    try:
        db = get_db()
        group_query = """
        SELECT id, group_name, project_title, compatibility_score,
               formation_date, status
        FROM groups WHERE id = ?
        """
        group = db.fetch_one(group_query, (group_id,))
        
        if not group:
            db.disconnect()
            return error_response("Group not found", 404)
        
        members_query = """
        SELECT s.id, s.student_number, s.first_name, s.last_name, 
               s.email, s.gwa, gm.role
        FROM students s
        JOIN group_members gm ON s.id = gm.student_id
        WHERE gm.group_id = ?
        ORDER BY gm.role DESC, s.last_name
        """
        group['members'] = db.fetch_all(members_query, (group_id,))
        
        tasks_query = """
        SELECT id, task_name, description, complexity_level,
               estimated_hours, deadline, status
        FROM tasks WHERE group_id = ?
        ORDER BY deadline
        """
        group['tasks'] = db.fetch_all(tasks_query, (group_id,))
        
        db.disconnect()
        return success_response(group, "Group details retrieved")
    except Exception as e:
        return error_response(f"Error fetching group: {str(e)}", 500)

@app.route('/api/groups/form', methods=['POST'])
def form_groups():
    """Trigger Matcher Agent to form groups"""
    try:
        data = request.get_json() or {}
        target_size = data.get('target_group_size', 4)
        algorithm = data.get('algorithm', 'ga')
        
        if data.get('clear_existing', False):
            db = get_db()
            db.execute_query("DELETE FROM task_assignments")
            db.execute_query("DELETE FROM tasks")
            db.execute_query("DELETE FROM group_members")
            db.execute_query("DELETE FROM groups")
            db.disconnect()
        
        if algorithm == 'ga':
            agent = MatcherAgentGA()
        else:
            from agents.matcher_agent import MatcherAgent
            agent = MatcherAgent()
        
        success = agent.run(target_group_size=target_size)
        
        if success:
            db = get_db()
            groups = db.fetch_all("SELECT * FROM groups ORDER BY id DESC")
            db.disconnect()
            
            return success_response(
                {'groups_formed': len(groups)},
                f"Successfully formed {len(groups)} groups using {algorithm.upper()} algorithm"
            )
        else:
            return error_response("Failed to form groups", 500)
    except Exception as e:
        return error_response(f"Error forming groups: {str(e)}", 500)

# ============================================================
# TASK ENDPOINTS
# ============================================================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        db = get_db()
        query = """
        SELECT t.*, g.group_name
        FROM tasks t
        JOIN groups g ON t.group_id = g.id
        WHERE 1=1
        """
        params = []
        
        if request.args.get('group_id'):
            query += " AND t.group_id = ?"
            params.append(request.args.get('group_id'))
        
        if request.args.get('status'):
            query += " AND t.status = ?"
            params.append(request.args.get('status'))
        
        query += " ORDER BY t.deadline"
        tasks = db.fetch_all(query, tuple(params) if params else None)
        db.disconnect()
        
        return success_response(tasks, f"Found {len(tasks)} tasks")
    except Exception as e:
        return error_response(f"Error fetching tasks: {str(e)}", 500)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create new task for a group"""
    try:
        data = request.get_json()
        required = ['group_id', 'task_name', 'estimated_hours', 'deadline']
        for field in required:
            if field not in data:
                return error_response(f"Missing required field: {field}")
        
        db = get_db()
        insert_query = """
        INSERT INTO tasks 
        (group_id, task_name, description, required_skills, 
         complexity_level, estimated_hours, deadline, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        task_id = db.insert_and_get_id(
            insert_query,
            (data['group_id'], data['task_name'], 
             data.get('description', ''),
             data.get('required_skills', ''),
             data.get('complexity_level', 'Medium'),
             data['estimated_hours'],
             data['deadline'],
             'Pending')
        )
        db.disconnect()
        
        if task_id:
            return success_response({'id': task_id}, "Task created successfully", 201)
        else:
            return error_response("Failed to create task", 500)
    except Exception as e:
        return error_response(f"Error creating task: {str(e)}", 500)

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update task status and completion"""
    try:
        data = request.get_json()
        db = get_db()
        
        if 'status' in data:
            update_query = "UPDATE tasks SET status = ? WHERE id = ?"
            db.execute_query(update_query, (data['status'], task_id))
        
        if 'completion_percentage' in data:
            update_assign_query = """
            UPDATE task_assignments 
            SET completion_percentage = ?, last_updated = CURRENT_TIMESTAMP
            WHERE task_id = ?
            """
            db.execute_query(update_assign_query, (data['completion_percentage'], task_id))
        
        db.disconnect()
        return success_response(None, "Task updated successfully")
    except Exception as e:
        return error_response(f"Error updating task: {str(e)}", 500)

# ============================================================
# DASHBOARD ENDPOINTS
# ============================================================

@app.route('/api/dashboard/faculty', methods=['GET'])
def faculty_dashboard():
    """Get analytics for faculty dashboard"""
    try:
        db = get_db()
        
        total_students = db.fetch_one("SELECT COUNT(*) as count FROM students")['count']
        total_groups = db.fetch_one("SELECT COUNT(*) as count FROM groups WHERE status = 'Active'")['count']
        total_tasks = db.fetch_one("SELECT COUNT(*) as count FROM tasks")['count']
        
        compat_stats = db.fetch_one("""
            SELECT AVG(compatibility_score) as avg_score,
                   MIN(compatibility_score) as min_score,
                   MAX(compatibility_score) as max_score
            FROM groups WHERE status = 'Active'
        """)
        
        task_stats = db.fetch_all("""
            SELECT status, COUNT(*) as count
            FROM tasks GROUP BY status
        """)
        
        at_risk = db.fetch_all("""
            SELECT g.id, g.group_name, COUNT(t.id) as task_count
            FROM groups g
            LEFT JOIN tasks t ON g.id = t.group_id
            WHERE g.status = 'Active'
            GROUP BY g.id
            HAVING task_count > 8
        """)
        
        db.disconnect()
        
        dashboard_data = {
            'summary': {
                'total_students': total_students,
                'total_groups': total_groups,
                'total_tasks': total_tasks
            },
            'compatibility': compat_stats,
            'task_distribution': task_stats,
            'at_risk_groups': at_risk
        }
        
        return success_response(dashboard_data, "Dashboard data retrieved")
    except Exception as e:
        return error_response(f"Error fetching dashboard data: {str(e)}", 500)

@app.route('/api/dashboard/student/<int:student_id>', methods=['GET'])
def student_dashboard(student_id):
    """Get dashboard data for a specific student"""
    try:
        db = get_db()
        
        group_query = """
        SELECT g.id, g.group_name, g.compatibility_score, gm.role
        FROM groups g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.student_id = ? AND g.status = 'Active'
        """
        student_group = db.fetch_one(group_query, (student_id,))
        
        if not student_group:
            db.disconnect()
            return success_response({'group': None, 'tasks': []}, "Student not assigned to any group")
        
        tasks_query = """
        SELECT t.id, t.task_name, t.description, t.estimated_hours,
               t.deadline, t.status, ta.completion_percentage
        FROM tasks t
        JOIN task_assignments ta ON t.id = ta.task_id
        WHERE ta.student_id = ?
        ORDER BY t.deadline
        """
        student_tasks = db.fetch_all(tasks_query, (student_id,))
        
        members_query = """
        SELECT s.id, s.first_name, s.last_name, gm.role
        FROM students s
        JOIN group_members gm ON s.id = gm.student_id
        WHERE gm.group_id = ?
        """
        group_members = db.fetch_all(members_query, (student_group['id'],))
        
        db.disconnect()
        
        dashboard_data = {
            'group': student_group,
            'tasks': student_tasks,
            'group_members': group_members,
            'total_hours': sum(t['estimated_hours'] for t in student_tasks)
        }
        
        return success_response(dashboard_data, "Student dashboard retrieved")
    except Exception as e:
        return error_response(f"Error fetching student dashboard: {str(e)}", 500)

# ============================================================
# HEALTH CHECK
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running"""
    return success_response({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }, "API is running")

# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", 500)

# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("MAS GROUP FORMATION SYSTEM - FULL STACK")
    print("=" * 60)
    print("Starting Flask application...")
    print("Web Interface: http://localhost:5000")
    print("API Base URL: http://localhost:5000/api")
    print("Press CTRL+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)