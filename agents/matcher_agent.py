from utils.db_connection import DatabaseConnection
import random
import math

class MatcherAgent:
    """
    Intelligent agent for forming balanced student groups
    Version 1: Simple weighted scoring approach
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.students = []
        self.groups = []
        self.min_group_size = 3
        self.max_group_size = 5
    
    def fetch_students(self):
        """
        Get all students with their complete profiles
        """
        print("\n[Matcher Agent] Fetching student data...")
        
        if not self.db.connect():
            print("Error: Could not connect to database")
            return False
        
        # Get basic student info
        query = """
        SELECT id, student_number, first_name, last_name, 
               email, gwa, year_level
        FROM students
        """
        self.students = self.db.fetch_all(query)
        
        if not self.students:
            print("Error: No students found in database")
            return False
        
        print(f"✓ Found {len(self.students)} students")
        
        # Fetch additional data for each student
        for student in self.students:
            student_id = student['id']
            
            # Get technical skills
            skills_query = """
            SELECT skill_name, proficiency_level, years_experience
            FROM technical_skills
            WHERE student_id = ?
            """
            student['skills'] = self.db.fetch_all(skills_query, (student_id,))
            
            # Get personality traits
            traits_query = """
            SELECT openness, conscientiousness, extraversion, 
                   agreeableness, neuroticism, learning_style
            FROM personality_traits
            WHERE student_id = ?
            """
            traits = self.db.fetch_one(traits_query, (student_id,))
            student['traits'] = traits if traits else {}
            
            # Get availability
            avail_query = """
            SELECT day_of_week, time_slot, is_available
            FROM availability
            WHERE student_id = ? AND is_available = 1
            """
            student['availability'] = self.db.fetch_all(avail_query, (student_id,))
        
        print(f"✓ Loaded complete profiles for all students")
        return True
    
    def calculate_skill_diversity(self, student1, student2):
        """
        Calculate how diverse two students' skills are
        Higher score = more complementary skills (good for learning)
        """
        skills1 = set([s['skill_name'] for s in student1['skills']])
        skills2 = set([s['skill_name'] for s in student2['skills']])
        
        if not skills1 or not skills2:
            return 0.5  # Neutral score if no skills data
        
        # How many unique skills between them
        total_skills = skills1.union(skills2)
        common_skills = skills1.intersection(skills2)
        
        # We want some overlap but also diversity
        # Perfect is 50% overlap, 50% unique
        overlap_ratio = len(common_skills) / len(total_skills) if total_skills else 0
        
        # Score is higher when ratio is around 0.5
        diversity_score = 1 - abs(overlap_ratio - 0.5) * 2
        
        return max(0, diversity_score)  # Ensure non-negative
    
    def calculate_gwa_balance(self, student1, student2):
        """
        Calculate GWA compatibility
        We want mixed ability groups (not all high or all low)
        """
        gwa1 = student1['gwa']
        gwa2 = student2['gwa']
        
        if gwa1 is None or gwa2 is None:
            return 0.5  # Neutral if no GWA data
        
        # Normalize GWA to 0-1 scale (1.0 is best, 5.0 is worst in PH system)
        # Flip it so higher is better
        norm_gwa1 = (5.0 - gwa1) / 4.0
        norm_gwa2 = (5.0 - gwa2) / 4.0
        
        # Calculate difference
        gwa_diff = abs(norm_gwa1 - norm_gwa2)
        
        # Moderate difference is good (0.2 to 0.5 range)
        if 0.2 <= gwa_diff <= 0.5:
            return 1.0  # Perfect balance
        elif gwa_diff < 0.2:
            return 0.7  # Too similar
        else:
            return 0.6  # Too different
    
    def calculate_schedule_overlap(self, student1, student2):
        """
        Calculate how much their schedules overlap
        Higher score = more common available times
        """
        # Create sets of available time slots
        avail1 = set([f"{a['day_of_week']}_{a['time_slot']}" 
                     for a in student1['availability']])
        avail2 = set([f"{a['day_of_week']}_{a['time_slot']}" 
                     for a in student2['availability']])
        
        if not avail1 or not avail2:
            return 0.5  # Neutral if no availability data
        
        # Calculate overlap percentage
        common_slots = avail1.intersection(avail2)
        total_possible = len(avail1.union(avail2))
        
        overlap_score = len(common_slots) / total_possible if total_possible > 0 else 0
        
        return overlap_score
    
    def calculate_personality_compatibility(self, student1, student2):
        """
        Calculate personality compatibility using Big Five traits
        Some traits should be similar, others different
        """
        traits1 = student1['traits']
        traits2 = student2['traits']
        
        if not traits1 or not traits2:
            return 0.5  # Neutral if no personality data
        
        # Conscientiousness should be similar (both should be responsible)
        consc_diff = abs(traits1.get('conscientiousness', 3) - 
                        traits2.get('conscientiousness', 3))
        consc_score = 1 - (consc_diff / 4.0)  # Normalize to 0-1
        
        # Agreeableness should be high for both (get along well)
        agree_avg = (traits1.get('agreeableness', 3) + 
                    traits2.get('agreeableness', 3)) / 2
        agree_score = agree_avg / 5.0  # Normalize to 0-1
        
        # Extraversion can be mixed (balance introverts and extroverts)
        extra_diff = abs(traits1.get('extraversion', 3) - 
                        traits2.get('extraversion', 3))
        extra_score = extra_diff / 4.0  # Higher diff is okay
        
        # Combine scores
        personality_score = (consc_score * 0.4 + agree_score * 0.4 + extra_score * 0.2)
        
        return personality_score
    
    def calculate_compatibility(self, student1, student2):
        """
        Calculate overall compatibility score between two students
        Combines multiple factors with weights
        """
        # Calculate individual components
        skill_score = self.calculate_skill_diversity(student1, student2)
        gwa_score = self.calculate_gwa_balance(student1, student2)
        schedule_score = self.calculate_schedule_overlap(student1, student2)
        personality_score = self.calculate_personality_compatibility(student1, student2)
        
        # Weighted combination (you can adjust these weights)
        weights = {
            'skills': 0.30,      # 30% - Important for task distribution
            'gwa': 0.20,         # 20% - Balanced ability
            'schedule': 0.30,    # 30% - Very important for meetings
            'personality': 0.20  # 20% - Important for team harmony
        }
        
        overall_score = (
            skill_score * weights['skills'] +
            gwa_score * weights['gwa'] +
            schedule_score * weights['schedule'] +
            personality_score * weights['personality']
        )
        
        return round(overall_score, 3)
    
    def create_compatibility_matrix(self):
        """
        Create a matrix of compatibility scores between all students
        """
        print("\n[Matcher Agent] Calculating compatibility matrix...")
        
        n = len(self.students)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                score = self.calculate_compatibility(self.students[i], self.students[j])
                matrix[i][j] = score
                matrix[j][i] = score  # Symmetric matrix
        
        print(f"✓ Compatibility matrix created ({n}x{n})")
        return matrix
    
    def form_groups_simple(self, target_group_size=4):
        """
        Simple grouping algorithm
        Forms groups by selecting most compatible students
        """
        print(f"\n[Matcher Agent] Forming groups (target size: {target_group_size})...")
        
        # Create compatibility matrix
        compat_matrix = self.create_compatibility_matrix()
        
        # Track which students are already grouped
        ungrouped = list(range(len(self.students)))
        groups = []
        group_num = 1
        
        while len(ungrouped) >= self.min_group_size:
            # Start a new group with a random student
            if len(ungrouped) < target_group_size:
                # Last group takes remaining students
                group = ungrouped.copy()
                ungrouped = []
            else:
                # Start with random student
                first_student = random.choice(ungrouped)
                group = [first_student]
                ungrouped.remove(first_student)
                
                # Add most compatible students
                while len(group) < target_group_size and ungrouped:
                    # Calculate average compatibility with current group
                    best_candidate = None
                    best_score = -1
                    
                    for candidate in ungrouped:
                        # Average compatibility with all group members
                        avg_compat = sum([compat_matrix[candidate][member] 
                                        for member in group]) / len(group)
                        
                        if avg_compat > best_score:
                            best_score = avg_compat
                            best_candidate = candidate
                    
                    if best_candidate is not None:
                        group.append(best_candidate)
                        ungrouped.remove(best_candidate)
            
            # Calculate group's average compatibility
            group_compat = 0
            count = 0
            for i in range(len(group)):
                for j in range(i + 1, len(group)):
                    group_compat += compat_matrix[group[i]][group[j]]
                    count += 1
            
            avg_compat = group_compat / count if count > 0 else 0
            
            groups.append({
                'group_num': group_num,
                'members': [self.students[idx] for idx in group],
                'compatibility_score': round(avg_compat, 3)
            })
            
            print(f"  Group {group_num}: {len(group)} members, "
                  f"compatibility: {avg_compat:.3f}")
            group_num += 1
        
        # Handle leftover students (if any)
        if ungrouped:
            print(f"\n  Note: {len(ungrouped)} students remain. "
                  f"Adding to smallest group...")
            smallest_group = min(groups, key=lambda g: len(g['members']))
            for idx in ungrouped:
                smallest_group['members'].append(self.students[idx])
        
        self.groups = groups
        print(f"\n✓ Formed {len(groups)} groups")
        return groups
    
    def save_groups_to_database(self):
        """
        Save formed groups to the database
        """
        print("\n[Matcher Agent] Saving groups to database...")
        
        saved_count = 0
        
        for group in self.groups:
            # Insert group
            group_query = """
            INSERT INTO groups (group_name, compatibility_score, status)
            VALUES (?, ?, ?)
            """
            group_name = f"Group {group['group_num']}"
            compat_score = group['compatibility_score']
            
            group_id = self.db.insert_and_get_id(
                group_query, 
                (group_name, compat_score, 'Active')
            )
            
            if group_id:
                # Insert group members
                for idx, member in enumerate(group['members']):
                    member_query = """
                    INSERT INTO group_members (group_id, student_id, role)
                    VALUES (?, ?, ?)
                    """
                    # First member is leader
                    role = 'Leader' if idx == 0 else 'Member'
                    
                    self.db.execute_query(
                        member_query,
                        (group_id, member['id'], role)
                    )
                
                saved_count += 1
        
        print(f"✓ Saved {saved_count} groups to database")
        return saved_count
    
    def run(self, target_group_size=4):
        """
        Main method to run the matcher agent
        """
        print("\n" + "=" * 60)
        print("MATCHER AGENT - SIMPLE VERSION")
        print("=" * 60)
        
        try:
            # Step 1: Fetch students
            if not self.fetch_students():
                return False
            
            # Step 2: Form groups
            groups = self.form_groups_simple(target_group_size)
            
            if not groups:
                print("Error: No groups formed")
                return False
            
            # Step 3: Save to database
            self.save_groups_to_database()
            
            # Step 4: Display summary
            print("\n" + "=" * 60)
            print("GROUP FORMATION SUMMARY")
            print("=" * 60)
            
            for group in groups:
                print(f"\n{group['group_num']}. Group {group['group_num']} "
                      f"(Compatibility: {group['compatibility_score']:.3f})")
                for member in group['members']:
                    print(f"   - {member['first_name']} {member['last_name']} "
                          f"(GWA: {member['gwa']})")
            
            print("\n" + "=" * 60)
            print("✓ MATCHER AGENT COMPLETED SUCCESSFULLY")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\nError in Matcher Agent: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.db.disconnect()

# Test the agent
if __name__ == "__main__":
    agent = MatcherAgent()
    agent.run(target_group_size=4)