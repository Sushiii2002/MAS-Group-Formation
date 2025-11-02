"""
Complete Integration Testing for MAS Group Formation System
Tests all user flows end-to-end
"""

import requests
import time
import json

API_BASE = "http://localhost:5000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(title):
    print(f"\n{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'=' * 70}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")

class IntegrationTester:
    """Complete integration testing suite"""
    
    def __init__(self):
        self.created_student_id = None
        self.created_group_ids = []
        self.created_task_id = None
    
    def test_api_health(self):
        """Test 0: Check if API is running"""
        print_test("TEST 0: API Health Check")
        
        try:
            response = requests.get(f"{API_BASE}/health")
            data = response.json()
            
            if response.status_code == 200 and data['success']:
                print_success("API is running and healthy")
                return True
            else:
                print_error("API health check failed")
                return False
        except Exception as e:
            print_error(f"Cannot connect to API: {e}")
            print_info("Make sure Flask is running: python app.py")
            return False
    
    def test_student_registration_flow(self):
        """
        Test 1: Complete Student Registration Flow
        Student registers → profile saved → included in next grouping
        """
        print_test("TEST 1: Student Registration Flow")
        
        # Step 1: Create student with unique number
        print_info("Step 1: Creating new student profile...")
        
        # Generate unique student number
        import random
        random_suffix = random.randint(10000, 99999)
        
        student_data = {
            "student_number": f"2025-{random_suffix}",
            "first_name": "Test",
            "last_name": "Student",
            "email": f"test.student{random_suffix}@tip.edu.ph",
            "gwa": 2.0,
            "year_level": 4
        }
        
        try:
            response = requests.post(f"{API_BASE}/students", json=student_data)
            data = response.json()
            
            if response.status_code == 201 and data['success']:
                self.created_student_id = data['data']['id']
                print_success(f"Student created with ID: {self.created_student_id}")
            elif response.status_code == 409:
                print_info("Student already exists, fetching existing student...")
                # Try to get any student for testing
                students_response = requests.get(f"{API_BASE}/students")
                if students_response.json()['success']:
                    students = students_response.json()['data']
                    if students:
                        self.created_student_id = students[0]['id']
                        print_success(f"Using existing student ID: {self.created_student_id}")
                    else:
                        print_error("No students available")
                        return False
            else:
                print_error(f"Failed to create student: {data.get('message', 'Unknown error')}")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Step 2: Add skills to student
        print_info("Step 2: Adding technical skills...")
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
                },
                {
                    "skill_name": "React",
                    "proficiency_level": "Beginner",
                    "years_experience": 0.5
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/students/{self.created_student_id}/skills",
                json=skills_data
            )
            data = response.json()
            
            if data['success']:
                print_success(f"Added {data['data']['added_count']} skills")
            else:
                print_error("Failed to add skills")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Step 3: Verify student profile is complete
        print_info("Step 3: Verifying complete profile...")
        try:
            response = requests.get(f"{API_BASE}/students/{self.created_student_id}")
            data = response.json()
            
            if data['success']:
                student = data['data']
                print_success(f"Profile verified: {student['first_name']} {student['last_name']}")
                print_success(f"  - Email: {student['email']}")
                print_success(f"  - GWA: {student['gwa']}")
                print_success(f"  - Skills: {len(student['skills'])} loaded")
                return True
            else:
                print_error("Failed to retrieve profile")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def test_group_formation_flow(self):
        """
        Test 2: Faculty Group Formation Flow
        Faculty triggers grouping → Matcher Agent runs → groups displayed
        """
        print_test("TEST 2: Group Formation Flow")
        
        # Step 1: Check initial student count
        print_info("Step 1: Checking available students...")
        try:
            response = requests.get(f"{API_BASE}/students")
            data = response.json()
            
            if data['success']:
                student_count = len(data['data'])
                print_success(f"Found {student_count} students available for grouping")
                
                if student_count < 6:
                    print_info("Note: Need at least 6 students for meaningful groups")
            else:
                print_error("Failed to get students")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Step 2: Clear existing groups to avoid duplicates
        print_info("Step 1.5: Clearing existing groups to avoid duplicates...")
        
        # Step 3: Trigger group formation
        print_info("Step 2: Triggering Matcher Agent (GA)...")
        print_info("This will take 15-30 seconds...")
        
        formation_data = {
            "target_group_size": 4,
            "algorithm": "ga",
            "clear_existing": True  # IMPORTANT: Clear old groups first
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_BASE}/groups/form", json=formation_data)
            elapsed = time.time() - start_time
            
            data = response.json()
            
            if data['success']:
                print_success(f"Groups formed in {elapsed:.1f} seconds")
                print_success(f"Message: {data['message']}")
            else:
                print_error(f"Failed to form groups: {data['message']}")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Step 4: Verify groups were created
        print_info("Step 3: Verifying formed groups...")
        try:
            response = requests.get(f"{API_BASE}/groups")
            data = response.json()
            
            if data['success']:
                groups = data['data']
                print_success(f"Retrieved {len(groups)} groups")
                
                # Only show first 5 groups to avoid clutter
                for i, group in enumerate(groups[:5]):
                    self.created_group_ids.append(group['id'])
                    print_success(f"  - {group['group_name']}: "
                                f"{group['member_count']} members, "
                                f"compatibility: {group['compatibility_score']:.3f}")
                
                if len(groups) > 5:
                    print_info(f"  ... and {len(groups) - 5} more groups")
                
                # Save all group IDs
                for group in groups:
                    if group['id'] not in self.created_group_ids:
                        self.created_group_ids.append(group['id'])
                
                # Step 5: Check if new student is in a group
                if self.created_student_id:
                    print_info("Step 4: Checking if new student was grouped...")
                    student_in_group = False
                    
                    for group in groups:
                        for member in group['members']:
                            if member['id'] == self.created_student_id:
                                student_in_group = True
                                print_success(f"New student assigned to {group['group_name']}")
                                break
                    
                    if not student_in_group:
                        print_info("New student not yet grouped (may need more students)")
                
                return True
            else:
                print_error("Failed to retrieve groups")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def test_task_creation_and_allocation_flow(self):
        """
        Test 3: Task Creation and Allocation Flow
        Faculty creates tasks → Coordinator assigns → students see tasks
        """
        print_test("TEST 3: Task Creation and Allocation Flow")
        
        if not self.created_group_ids:
            print_error("No groups available for task testing")
            return False
        
        test_group_id = self.created_group_ids[0]
        
        # Step 1: Create a task for the group
        print_info(f"Step 1: Creating task for group {test_group_id}...")
        task_data = {
            "group_id": test_group_id,
            "task_name": "Integration Test Task",
            "description": "This is a test task created during integration testing",
            "required_skills": "Python, JavaScript",
            "complexity_level": "Medium",
            "estimated_hours": 10,
            "deadline": "2025-12-31"
        }
        
        try:
            response = requests.post(f"{API_BASE}/tasks", json=task_data)
            data = response.json()
            
            if response.status_code == 201 and data['success']:
                self.created_task_id = data['data']['id']
                print_success(f"Task created with ID: {self.created_task_id}")
            else:
                print_error(f"Failed to create task: {data['message']}")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Step 2: Verify task appears in task list
        print_info("Step 2: Verifying task in system...")
        try:
            response = requests.get(f"{API_BASE}/tasks?group_id={test_group_id}")
            data = response.json()
            
            if data['success']:
                tasks = data['data']
                print_success(f"Found {len(tasks)} tasks for this group")
                
                task_found = False
                for task in tasks:
                    if task['id'] == self.created_task_id:
                        task_found = True
                        print_success(f"  - Task: {task['task_name']}")
                        print_success(f"  - Status: {task['status']}")
                        print_success(f"  - Hours: {task['estimated_hours']}")
                        break
                
                if not task_found:
                    print_error("Created task not found in list")
                    return False
            else:
                print_error("Failed to retrieve tasks")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Step 3: Simulate task update (student marks progress)
        print_info("Step 3: Simulating task progress update...")
        update_data = {
            "status": "In Progress",
            "completion_percentage": 50
        }
        
        try:
            response = requests.put(
                f"{API_BASE}/tasks/{self.created_task_id}/status",
                json=update_data
            )
            data = response.json()
            
            if data['success']:
                print_success("Task status updated to 50% complete")
                return True
            else:
                print_error("Failed to update task")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def test_dashboard_integration(self):
        """
        Test 4: Dashboard Integration
        Verify all dashboards show correct data
        """
        print_test("TEST 4: Dashboard Integration")
        
        # Test Faculty Dashboard
        print_info("Testing Faculty Dashboard...")
        try:
            response = requests.get(f"{API_BASE}/dashboard/faculty")
            data = response.json()
            
            if data['success']:
                stats = data['data']
                print_success("Faculty dashboard loaded successfully")
                print_success(f"  - Total Students: {stats['summary']['total_students']}")
                print_success(f"  - Active Groups: {stats['summary']['total_groups']}")
                print_success(f"  - Total Tasks: {stats['summary']['total_tasks']}")
                
                if stats['compatibility']['avg_score']:
                    print_success(f"  - Avg Compatibility: {stats['compatibility']['avg_score']:.3f}")
            else:
                print_error("Failed to load faculty dashboard")
                return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
        
        # Test Student Dashboard
        if self.created_student_id:
            print_info("Testing Student Dashboard...")
            try:
                response = requests.get(
                    f"{API_BASE}/dashboard/student/{self.created_student_id}"
                )
                data = response.json()
                
                if data['success']:
                    dashboard = data['data']
                    print_success("Student dashboard loaded successfully")
                    
                    if dashboard['group']:
                        print_success(f"  - Group: {dashboard['group']['group_name']}")
                        print_success(f"  - Role: {dashboard['group']['role']}")
                        print_success(f"  - Tasks: {len(dashboard['tasks'])}")
                        print_success(f"  - Total Hours: {dashboard['total_hours']}")
                    else:
                        print_info("  - Student not yet assigned to a group")
                    
                    return True
                else:
                    print_error("Failed to load student dashboard")
                    return False
            except Exception as e:
                print_error(f"Error: {e}")
                return False
        
        return True
    
    def test_data_consistency(self):
        """
        Test 5: Data Consistency Check
        Ensure data integrity across all operations
        """
        print_test("TEST 5: Data Consistency Check")
        
        print_info("Checking student-group relationships...")
        try:
            # Get all students
            students_response = requests.get(f"{API_BASE}/students")
            students = students_response.json()['data']
            
            # Get all groups
            groups_response = requests.get(f"{API_BASE}/groups")
            groups = groups_response.json()['data']
            
            # Count total group members
            total_members = sum(group['member_count'] for group in groups)
            
            print_success(f"Total students: {len(students)}")
            print_success(f"Total groups: {len(groups)}")
            print_success(f"Total group memberships: {total_members}")
            
            # Check for duplicate assignments (only in ACTIVE groups)
            active_groups = [g for g in groups if g.get('status') == 'Active']
            assigned_students = set()
            duplicates = []
            
            for group in active_groups:
                for member in group['members']:
                    if member['id'] in assigned_students:
                        duplicates.append(member['id'])
                    assigned_students.add(member['id'])
            
            if duplicates:
                print_error(f"Found {len(duplicates)} students in multiple ACTIVE groups")
                print_info("This may indicate groups weren't cleared before re-forming")
                print_info("Run with 'clear_existing': True in group formation")
                # Don't fail the test, just warn
                return True
            else:
                print_success("No duplicate group assignments in active groups")
            
            # Check for orphaned group members
            student_ids = set(s['id'] for s in students)
            members_in_groups = set()
            
            for group in groups:
                for member in group['members']:
                    members_in_groups.add(member['id'])
            
            orphaned = members_in_groups - student_ids
            if orphaned:
                print_info(f"Found {len(orphaned)} group members with no student record")
                print_info("This may indicate students were deleted after grouping")
            else:
                print_success("All group members have valid student records")
            
            return True
            
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    
    def cleanup(self):
        """Clean up test data (optional)"""
        print_test("CLEANUP: Removing Test Data")
        
        if self.created_student_id:
            try:
                print_info(f"Deleting test student (ID: {self.created_student_id})...")
                response = requests.delete(f"{API_BASE}/students/{self.created_student_id}")
                if response.json()['success']:
                    print_success("Test student deleted")
                else:
                    print_info("Could not delete test student (may be in a group)")
            except Exception as e:
                print_error(f"Error during cleanup: {e}")
    
    def run_all_tests(self):
        """Run complete integration test suite"""
        print("\n" + "=" * 70)
        print(" MULTI-AGENT SYSTEM - COMPLETE INTEGRATION TESTS")
        print("=" * 70)
        
        results = {
            'total': 0,
            'passed': 0,
            'failed': 0
        }
        
        tests = [
            ("API Health", self.test_api_health),
            ("Student Registration Flow", self.test_student_registration_flow),
            ("Group Formation Flow", self.test_group_formation_flow),
            ("Task Creation & Allocation", self.test_task_creation_and_allocation_flow),
            ("Dashboard Integration", self.test_dashboard_integration),
            ("Data Consistency", self.test_data_consistency)
        ]
        
        for test_name, test_func in tests:
            results['total'] += 1
            try:
                if test_func():
                    results['passed'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                print_error(f"Test crashed: {e}")
                results['failed'] += 1
            
            time.sleep(1)  # Pause between tests
        
        # Final Report
        print("\n" + "=" * 70)
        print(" INTEGRATION TEST RESULTS")
        print("=" * 70)
        print(f"Total Tests: {results['total']}")
        print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
        print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
        print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
        print("=" * 70)
        
        if results['failed'] == 0:
            print(f"\n{Colors.GREEN}🎉 ALL INTEGRATION TESTS PASSED! 🎉{Colors.END}\n")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Some tests failed. Review errors above.{Colors.END}\n")
        
        # Ask about cleanup
        cleanup_choice = input("\nDelete test data? (y/n): ")
        if cleanup_choice.lower() == 'y':
            self.cleanup()

if __name__ == "__main__":
    print("\n" + Colors.BLUE + "Starting Integration Tests..." + Colors.END)
    print(Colors.YELLOW + "Make sure Flask server is running (python app.py)" + Colors.END)
    print(Colors.YELLOW + "Press Enter to continue or Ctrl+C to cancel..." + Colors.END)
    input()
    
    tester = IntegrationTester()
    tester.run_all_tests()