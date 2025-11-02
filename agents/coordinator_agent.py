from utils.db_connection import DatabaseConnection
import random
from datetime import datetime, timedelta

class CoordinatorAgent:
    """
    Intelligent agent for task allocation and workload management
    Assigns tasks based on skills and balances workload
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.groups = []
        self.workload_threshold = 0.15  # 15% variance allowed
    
    def fetch_groups(self):
        """Fetch all active groups with their members"""
        print("\n[Coordinator Agent] Fetching active groups...")
        
        if not self.db.connect():
            print("Error: Could not connect to database")
            return False
        
        # Get all active groups
        groups_query = """
        SELECT id, group_name, compatibility_score
        FROM groups
        WHERE status = 'Active'
        """
        groups = self.db.fetch_all(groups_query)
        
        if not groups:
            print("Error: No active groups found")
            return False
        
        print(f"✓ Found {len(groups)} active groups")
        
        # Fetch members for each group
        for group in groups:
            members_query = """
            SELECT s.id, s.first_name, s.last_name, s.gwa,
                   gm.role
            FROM students s
            JOIN group_members gm ON s.id = gm.student_id
            WHERE gm.group_id = ?
            """
            members = self.db.fetch_all(members_query, (group['id'],))
            
            # Fetch skills for each member
            for member in members:
                skills_query = """
                SELECT skill_name, proficiency_level, years_experience
                FROM technical_skills
                WHERE student_id = ?
                """
                member['skills'] = self.db.fetch_all(skills_query, (member['id'],))
                member['current_workload'] = 0  # Will calculate later
            
            group['members'] = members
        
        self.groups = groups
        print(f"✓ Loaded {sum(len(g['members']) for g in groups)} total members")
        return True
    
    def create_sample_tasks(self, group_id, num_tasks=6):
        """
        Create sample tasks for a group
        In real implementation, faculty would create these
        """
        print(f"\n[Coordinator Agent] Creating sample tasks for group {group_id}...")
        
        task_templates = [
            {
                'name': 'Database Design',
                'description': 'Design and implement database schema',
                'required_skills': ['MySQL', 'Database Design', 'SQL'],
                'complexity': 'High',
                'estimated_hours': 20
            },
            {
                'name': 'Backend API Development',
                'description': 'Develop REST API endpoints',
                'required_skills': ['Python', 'Flask', 'REST APIs'],
                'complexity': 'High',
                'estimated_hours': 25
            },
            {
                'name': 'Frontend Interface',
                'description': 'Create user interface with HTML/CSS/JS',
                'required_skills': ['HTML/CSS', 'JavaScript', 'React'],
                'complexity': 'Medium',
                'estimated_hours': 18
            },
            {
                'name': 'Authentication System',
                'description': 'Implement user login and security',
                'required_skills': ['Python', 'Security', 'Authentication'],
                'complexity': 'Medium',
                'estimated_hours': 15
            },
            {
                'name': 'Testing and QA',
                'description': 'Write tests and ensure quality',
                'required_skills': ['Testing', 'Python', 'Quality Assurance'],
                'complexity': 'Low',
                'estimated_hours': 12
            },
            {
                'name': 'Documentation',
                'description': 'Write technical documentation',
                'required_skills': ['Technical Writing', 'Documentation'],
                'complexity': 'Low',
                'estimated_hours': 10
            }
        ]
        
        # Select random tasks
        selected_tasks = random.sample(task_templates, min(num_tasks, len(task_templates)))
        
        created_tasks = []
        for task in selected_tasks:
            # Calculate deadline (2-4 weeks from now)
            days_ahead = random.randint(14, 28)
            deadline = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            query = """
            INSERT INTO tasks 
            (group_id, task_name, description, required_skills, 
             complexity_level, estimated_hours, deadline, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                group_id,
                task['name'],
                task['description'],
                ', '.join(task['required_skills']),
                task['complexity'],
                task['estimated_hours'],
                deadline,
                'Pending'
            )
            
            task_id = self.db.insert_and_get_id(query, params)
            
            if task_id:
                task['id'] = task_id
                created_tasks.append(task)
        
        print(f"✓ Created {len(created_tasks)} tasks")
        return created_tasks
    
    def calculate_skill_match(self, member, task):
        """
        Calculate how well a member's skills match a task
        Returns score from 0 to 1
        """
        if not task.get('required_skills'):
            return 0.5  # Neutral if no specific skills required
        
        required = set(task['required_skills'])
        member_skills = {s['skill_name']: s for s in member['skills']}
        
        if not member_skills:
            return 0.1  # Very low if member has no skills listed
        
        match_score = 0
        for skill in required:
            if skill in member_skills:
                # Higher score for higher proficiency
                proficiency = member_skills[skill]['proficiency_level']
                if proficiency == 'Expert':
                    match_score += 1.0
                elif proficiency == 'Advanced':
                    match_score += 0.8
                elif proficiency == 'Intermediate':
                    match_score += 0.6
                elif proficiency == 'Beginner':
                    match_score += 0.3
        
        # Normalize by number of required skills
        final_score = match_score / len(required) if required else 0
        return min(final_score, 1.0)  # Cap at 1.0
    
    def allocate_tasks(self, group):
        """
        Allocate tasks to group members based on skills
        Uses greedy algorithm with workload balancing
        """
        print(f"\n[Coordinator Agent] Allocating tasks for {group['group_name']}...")
        
        # Fetch tasks for this group
        tasks_query = """
        SELECT id, task_name, description, required_skills,
               complexity_level, estimated_hours, deadline
        FROM tasks
        WHERE group_id = ? AND status = 'Pending'
        """
        tasks = self.db.fetch_all(tasks_query, (group['id'],))
        
        if not tasks:
            print("  No pending tasks found")
            return []
        
        # Parse required skills
        for task in tasks:
            if task['required_skills']:
                task['required_skills'] = [s.strip() for s in task['required_skills'].split(',')]
            else:
                task['required_skills'] = []
        
        # Initialize workload for each member
        members = group['members']
        for member in members:
            member['assigned_hours'] = 0
            member['assigned_tasks'] = []
        
        # Sort tasks by complexity (high to low)
        complexity_order = {'High': 3, 'Medium': 2, 'Low': 1}
        tasks_sorted = sorted(tasks, 
                             key=lambda t: complexity_order.get(t['complexity_level'], 0),
                             reverse=True)
        
        allocations = []
        
        # Allocate each task
        for task in tasks_sorted:
            # Calculate skill match for each member
            candidates = []
            for member in members:
                skill_match = self.calculate_skill_match(member, task)
                
                # Consider current workload
                avg_workload = sum(m['assigned_hours'] for m in members) / len(members)
                workload_factor = 1 - (member['assigned_hours'] / (avg_workload + 0.1))
                
                # Combined score
                score = skill_match * 0.7 + workload_factor * 0.3
                
                candidates.append({
                    'member': member,
                    'score': score,
                    'skill_match': skill_match
                })
            
            # Select best candidate
            best_candidate = max(candidates, key=lambda c: c['score'])
            selected_member = best_candidate['member']
            
            # Assign task
            assignment_query = """
            INSERT INTO task_assignments 
            (task_id, student_id, status, completion_percentage)
            VALUES (?, ?, ?, ?)
            """
            
            self.db.execute_query(
                assignment_query,
                (task['id'], selected_member['id'], 'Assigned', 0)
            )
            
            # Update task status
            update_task_query = """
            UPDATE tasks SET status = 'In Progress' WHERE id = ?
            """
            self.db.execute_query(update_task_query, (task['id'],))
            
            # Update member's workload
            selected_member['assigned_hours'] += task['estimated_hours']
            selected_member['assigned_tasks'].append(task)
            
            allocations.append({
                'task': task['task_name'],
                'assignee': f"{selected_member['first_name']} {selected_member['last_name']}",
                'skill_match': best_candidate['skill_match'],
                'hours': task['estimated_hours']
            })
            
            print(f"  ✓ {task['task_name']} → {selected_member['first_name']} "
                  f"(skill match: {best_candidate['skill_match']:.2f})")
        
        # Check workload balance
        total_hours = sum(m['assigned_hours'] for m in members)
        avg_hours = total_hours / len(members)
        
        print(f"\n  Workload Distribution:")
        for member in members:
            variance = (member['assigned_hours'] - avg_hours) / avg_hours if avg_hours > 0 else 0
            status = "⚠️" if abs(variance) > self.workload_threshold else "✓"
            print(f"    {status} {member['first_name']}: {member['assigned_hours']:.1f} hours "
                  f"({variance:+.1%} from average)")
        
        return allocations
    
    def flag_at_risk_groups(self):
        """
        Identify groups that might be struggling
        Based on workload imbalance or incomplete tasks
        """
        print("\n[Coordinator Agent] Checking for at-risk groups...")
        
        at_risk = []
        
        for group in self.groups:
            risks = []
            
            # Check workload balance
            members = group['members']
            if len(members) > 1:
                total_hours = sum(m.get('assigned_hours', 0) for m in members)
                avg_hours = total_hours / len(members)
                
                for member in members:
                    variance = abs(member.get('assigned_hours', 0) - avg_hours) / avg_hours if avg_hours > 0 else 0
                    if variance > self.workload_threshold:
                        risks.append(f"Workload imbalance: {member['first_name']} has {variance:.1%} variance")
            
            # Check for overdue tasks (in real system)
            # This would check actual dates
            
            if risks:
                at_risk.append({
                    'group': group['group_name'],
                    'risks': risks
                })
        
        if at_risk:
            print(f"  ⚠️ Found {len(at_risk)} at-risk groups:")
            for item in at_risk:
                print(f"    - {item['group']}")
                for risk in item['risks']:
                    print(f"        • {risk}")
        else:
            print("  ✓ All groups have balanced workloads")
        
        return at_risk
    
    def run(self, create_tasks=True):
        """Main method to run coordinator agent"""
        print("\n" + "=" * 60)
        print("COORDINATOR AGENT - TASK ALLOCATION")
        print("=" * 60)
        
        try:
            # Step 1: Fetch groups
            if not self.fetch_groups():
                return False
            
            # Step 2: For each group, create tasks and allocate
            for group in self.groups:
                if create_tasks:
                    self.create_sample_tasks(group['id'])
                
                self.allocate_tasks(group)
            
            # Step 3: Flag at-risk groups
            self.flag_at_risk_groups()
            
            print("\n" + "=" * 60)
            print("✓ COORDINATOR AGENT COMPLETED SUCCESSFULLY")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\nError in Coordinator Agent: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.db.disconnect()

# Test the coordinator agent
if __name__ == "__main__":
    agent = CoordinatorAgent()
    agent.run(create_tasks=True)