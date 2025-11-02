import requests
import json

BASE_URL = "http://localhost:5000/api"

def print_response(title, response):
    """Pretty print API response"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_health_check():
    """Test if API is running"""
    response = requests.get(f"{BASE_URL}/health")
    print_response("1. HEALTH CHECK", response)

def test_get_students():
    """Test getting all students"""
    response = requests.get(f"{BASE_URL}/students")
    print_response("2. GET ALL STUDENTS", response)
    return response.json()['data']

def test_get_student_profile():
    """Test getting single student profile"""
    response = requests.get(f"{BASE_URL}/students/1")
    print_response("3. GET STUDENT PROFILE", response)

def test_create_student():
    """Test creating a new student"""
    new_student = {
        "student_number": "2021-99999",
        "first_name": "Test",
        "last_name": "Student",
        "email": "test.student@tip.edu.ph",
        "gwa": 1.75,
        "year_level": 4
    }
    
    response = requests.post(f"{BASE_URL}/students", json=new_student)
    print_response("4. CREATE NEW STUDENT", response)
    
    if response.status_code == 201:
        return response.json()['data']['id']
    return None

def test_add_skills(student_id):
    """Test adding skills to student"""
    skills_data = {
        "skills": [
            {
                "skill_name": "Python",
                "proficiency_level": "Advanced",
                "years_experience": 2.5
            },
            {
                "skill_name": "JavaScript",
                "proficiency_level": "Intermediate",
                "years_experience": 1.5
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/students/{student_id}/skills", json=skills_data)
    print_response("5. ADD STUDENT SKILLS", response)

def test_form_groups():
    """Test triggering group formation"""
    form_data = {
        "target_group_size": 4,
        "algorithm": "ga",
        "clear_existing": False
    }
    
    response = requests.post(f"{BASE_URL}/groups/form", json=form_data)
    print_response("6. FORM GROUPS (GA)", response)

def test_get_groups():
    """Test getting all groups"""
    response = requests.get(f"{BASE_URL}/groups")
    print_response("7. GET ALL GROUPS", response)
    return response.json()['data']

def test_get_group_details(group_id):
    """Test getting single group details"""
    response = requests.get(f"{BASE_URL}/groups/{group_id}")
    print_response("8. GET GROUP DETAILS", response)

def test_create_task(group_id):
    """Test creating a task"""
    task_data = {
        "group_id": group_id,
        "task_name": "API Development",
        "description": "Develop REST API endpoints",
        "required_skills": "Python, Flask, REST APIs",
        "complexity_level": "High",
        "estimated_hours": 25,
        "deadline": "2025-12-31"
    }
    
    response = requests.post(f"{BASE_URL}/tasks", json=task_data)
    print_response("9. CREATE TASK", response)
    
    if response.status_code == 201:
        return response.json()['data']['id']
    return None

def test_get_tasks():
    """Test getting all tasks"""
    response = requests.get(f"{BASE_URL}/tasks")
    print_response("10. GET ALL TASKS", response)

def test_update_task_status(task_id):
    """Test updating task status"""
    update_data = {
        "status": "In Progress",
        "completion_percentage": 50
    }
    
    response = requests.put(f"{BASE_URL}/tasks/{task_id}/status", json=update_data)
    print_response("11. UPDATE TASK STATUS", response)

def test_faculty_dashboard():
    """Test faculty dashboard"""
    response = requests.get(f"{BASE_URL}/dashboard/faculty")
    print_response("12. FACULTY DASHBOARD", response)

def test_student_dashboard(student_id):
    """Test student dashboard"""
    response = requests.get(f"{BASE_URL}/dashboard/student/{student_id}")
    print_response("13. STUDENT DASHBOARD", response)

def run_all_tests():
    """Run all API tests in sequence"""
    print("\n" + "=" * 60)
    print("STARTING API TESTS")
    print("Make sure Flask server is running on http://localhost:5000")
    print("=" * 60)
    
    try:
        # Basic tests
        test_health_check()
        students = test_get_students()
        test_get_student_profile()
        
        # Create new student
        new_student_id = test_create_student()
        if new_student_id:
            test_add_skills(new_student_id)
        
        # Group tests
        test_form_groups()
        groups = test_get_groups()
        
        if groups and len(groups) > 0:
            test_get_group_details(groups[0]['id'])
            
            # Task tests
            task_id = test_create_task(groups[0]['id'])
            test_get_tasks()
            
            if task_id:
                test_update_task_status(task_id)
        
        # Dashboard tests
        test_faculty_dashboard()
        if students and len(students) > 0:
            test_student_dashboard(students[0]['id'])
        
        print("\n" + "=" * 60)
        print("✓ ALL API TESTS COMPLETED")
        print("=" * 60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to API server")
        print("Make sure Flask is running: python app.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()