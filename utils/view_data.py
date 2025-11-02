from db_connection import DatabaseConnection

def view_sample_data():
    """Display sample data from the database"""
    
    db = DatabaseConnection()
    db.connect()
    
    print("\n=== SAMPLE STUDENTS ===")
    students = db.fetch_all("SELECT * FROM students LIMIT 5")
    for s in students:
        print(f"{s['id']}. {s['first_name']} {s['last_name']} (GWA: {s['gwa']})")
    
    print("\n=== SAMPLE SKILLS ===")
    skills = db.fetch_all("""
        SELECT s.first_name, s.last_name, ts.skill_name, ts.proficiency_level
        FROM students s
        JOIN technical_skills ts ON s.id = ts.student_id
        LIMIT 10
    """)
    for sk in skills:
        print(f"{sk['first_name']} {sk['last_name']}: {sk['skill_name']} ({sk['proficiency_level']})")
    
    print("\n=== SAMPLE PERSONALITY ===")
    traits = db.fetch_all("""
        SELECT s.first_name, s.last_name, p.extraversion, p.conscientiousness, p.learning_style
        FROM students s
        JOIN personality_traits p ON s.id = p.student_id
        LIMIT 5
    """)
    for t in traits:
        print(f"{t['first_name']}: Extraversion={t['extraversion']}, Conscientiousness={t['conscientiousness']}, Style={t['learning_style']}")
    
    db.disconnect()

if __name__ == "__main__":
    view_sample_data()