from db_connection import DatabaseConnection
import random
from datetime import datetime, timedelta

class TestDataPopulator:
    """
    Populates SQLite database with realistic test data for development
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.student_ids = []  # Will store created student IDs
        
    def generate_students(self, count=20):
        """Create test student records"""
        
        first_names = ['Juan', 'Maria', 'Jose', 'Anna', 'Miguel', 'Sofia', 
                      'Carlos', 'Isabella', 'Rafael', 'Gabriela', 'Diego',
                      'Camila', 'Luis', 'Valentina', 'Pedro', 'Elena',
                      'Marco', 'Julia', 'Rico', 'Lucia']
        
        last_names = ['Santos', 'Reyes', 'Cruz', 'Garcia', 'Martinez',
                     'Rodriguez', 'Fernandez', 'Lopez', 'Gonzales', 'Perez',
                     'Sanchez', 'Ramirez', 'Torres', 'Flores', 'Rivera',
                     'Gomez', 'Diaz', 'Morales', 'Mendoza', 'Castillo']
        
        print(f"\nCreating {count} test students...")
        
        for i in range(count):
            student_number = f"2021-{random.randint(10000, 99999)}"
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@tip.edu.ph"
            gwa = round(random.uniform(1.25, 3.50), 2)
            year_level = random.randint(3, 4)  # 3rd or 4th year for capstone
            
            query = """
            INSERT INTO students 
            (student_number, first_name, last_name, email, gwa, year_level, program)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            # SQLite uses ? instead of %s for parameters
            params = (student_number, first_name, last_name, email, 
                     gwa, year_level, 'Computer Science')
            
            student_id = self.db.insert_and_get_id(query, params)
            if student_id:
                self.student_ids.append(student_id)
        
        print(f"✓ Created {len(self.student_ids)} students")
    
    def generate_technical_skills(self):
        """Add technical skills for each student"""
        
        skills = [
            'Python', 'Java', 'JavaScript', 'HTML/CSS', 'React',
            'Node.js', 'MySQL', 'MongoDB', 'Git', 'Docker',
            'Flask', 'Django', 'Spring Boot', 'REST APIs', 'Agile'
        ]
        
        proficiency_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
        
        print("\nAdding technical skills...")
        
        for student_id in self.student_ids:
            # Each student gets 4-8 random skills
            num_skills = random.randint(4, 8)
            student_skills = random.sample(skills, num_skills)
            
            for skill in student_skills:
                proficiency = random.choice(proficiency_levels)
                years = round(random.uniform(0.5, 4.0), 1)
                
                query = """
                INSERT INTO technical_skills 
                (student_id, skill_name, proficiency_level, years_experience)
                VALUES (?, ?, ?, ?)
                """
                
                params = (student_id, skill, proficiency, years)
                self.db.execute_query(query, params)
        
        print(f"✓ Added skills for {len(self.student_ids)} students")
    
    def generate_personality_traits(self):
        """Add personality traits for each student"""
        
        learning_styles = ['Visual', 'Auditory', 'Reading/Writing', 'Kinesthetic']
        
        print("\nAdding personality traits...")
        
        for student_id in self.student_ids:
            # Random Big Five scores (1-5)
            openness = random.randint(2, 5)
            conscientiousness = random.randint(2, 5)
            extraversion = random.randint(1, 5)
            agreeableness = random.randint(2, 5)
            neuroticism = random.randint(1, 4)
            learning_style = random.choice(learning_styles)
            
            query = """
            INSERT INTO personality_traits 
            (student_id, openness, conscientiousness, extraversion, 
             agreeableness, neuroticism, learning_style)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (student_id, openness, conscientiousness, extraversion,
                     agreeableness, neuroticism, learning_style)
            
            self.db.execute_query(query, params)
        
        print(f"✓ Added personality data for {len(self.student_ids)} students")
    
    def generate_availability(self):
        """Add schedule availability for each student"""
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        time_slots = ['8:00-10:00', '10:00-12:00', '13:00-15:00', 
                     '15:00-17:00', '17:00-19:00', '19:00-21:00']
        
        print("\nAdding schedule availability...")
        
        for student_id in self.student_ids:
            # Each student available 60-80% of time slots
            for day in days:
                for time_slot in time_slots:
                    is_available = 1 if random.random() < 0.7 else 0  # SQLite uses 1/0 for boolean
                    
                    query = """
                    INSERT INTO availability 
                    (student_id, day_of_week, time_slot, is_available)
                    VALUES (?, ?, ?, ?)
                    """
                    
                    params = (student_id, day, time_slot, is_available)
                    self.db.execute_query(query, params)
        
        print(f"✓ Added availability for {len(self.student_ids)} students")
    
    def populate_all(self, student_count=20):
        """Run all population methods"""
        
        print("\n" + "=" * 60)
        print("POPULATING TEST DATA")
        print("=" * 60)
        
        if not self.db.connect():
            print("Failed to connect to database!")
            return
        
        try:
            self.generate_students(student_count)
            self.generate_technical_skills()
            self.generate_personality_traits()
            self.generate_availability()
            
            # Display summary
            print("\n" + "=" * 60)
            print("DATA SUMMARY")
            print("=" * 60)
            
            total_students = self.db.fetch_one("SELECT COUNT(*) as count FROM students")
            total_skills = self.db.fetch_one("SELECT COUNT(*) as count FROM technical_skills")
            total_traits = self.db.fetch_one("SELECT COUNT(*) as count FROM personality_traits")
            total_avail = self.db.fetch_one("SELECT COUNT(*) as count FROM availability")
            
            print(f"Total Students: {total_students['count']}")
            print(f"Total Skills: {total_skills['count']}")
            print(f"Total Personality Records: {total_traits['count']}")
            print(f"Total Availability Slots: {total_avail['count']}")
            
            print("\n" + "=" * 60)
            print("✓ ALL TEST DATA CREATED SUCCESSFULLY!")
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"Error during population: {e}")
        
        finally:
            self.db.disconnect()

# Run the script
if __name__ == "__main__":
    populator = TestDataPopulator()
    populator.populate_all(student_count=20)  # Change number as needed