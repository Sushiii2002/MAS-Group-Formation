"""
Database Cleanup Utility
Use this to clean up test data and reset the database
"""

from utils.db_connection import DatabaseConnection

def cleanup_all_groups():
    """Remove all groups and related data"""
    db = DatabaseConnection()
    db.connect()
    
    print("\n" + "=" * 60)
    print("DATABASE CLEANUP - GROUPS")
    print("=" * 60)
    
    # Get counts before cleanup
    groups_before = db.fetch_one("SELECT COUNT(*) as count FROM groups")['count']
    members_before = db.fetch_one("SELECT COUNT(*) as count FROM group_members")['count']
    tasks_before = db.fetch_one("SELECT COUNT(*) as count FROM tasks")['count']
    
    print(f"\nBefore cleanup:")
    print(f"  - Groups: {groups_before}")
    print(f"  - Group members: {members_before}")
    print(f"  - Tasks: {tasks_before}")
    
    # Delete in correct order (foreign key constraints)
    print("\nDeleting data...")
    db.execute_query("DELETE FROM task_assignments")
    print("  ✓ Cleared task assignments")
    
    db.execute_query("DELETE FROM tasks")
    print("  ✓ Cleared tasks")
    
    db.execute_query("DELETE FROM group_members")
    print("  ✓ Cleared group members")
    
    db.execute_query("DELETE FROM groups")
    print("  ✓ Cleared groups")
    
    # Verify cleanup
    groups_after = db.fetch_one("SELECT COUNT(*) as count FROM groups")['count']
    
    print(f"\nAfter cleanup:")
    print(f"  - Groups: {groups_after}")
    print(f"  - Group members: 0")
    print(f"  - Tasks: 0")
    
    print("\n" + "=" * 60)
    print("✓ CLEANUP COMPLETED")
    print("=" * 60 + "\n")
    
    db.disconnect()

def cleanup_test_students():
    """Remove test students (those with student numbers starting with 2025-)"""
    db = DatabaseConnection()
    db.connect()
    
    print("\n" + "=" * 60)
    print("DATABASE CLEANUP - TEST STUDENTS")
    print("=" * 60)
    
    # Find test students
    test_students = db.fetch_all(
        "SELECT id, student_number, first_name, last_name FROM students WHERE student_number LIKE '2025-%'"
    )
    
    print(f"\nFound {len(test_students)} test students:")
    for student in test_students:
        print(f"  - {student['student_number']}: {student['first_name']} {student['last_name']}")
    
    if test_students:
        confirm = input("\nDelete these students? (y/n): ")
        if confirm.lower() == 'y':
            for student in test_students:
                db.execute_query("DELETE FROM students WHERE id = ?", (student['id'],))
            print(f"\n✓ Deleted {len(test_students)} test students")
        else:
            print("\nCancelled")
    else:
        print("\nNo test students to delete")
    
    print("\n" + "=" * 60)
    
    db.disconnect()

def reset_database():
    """Complete database reset (keep schema, clear all data)"""
    db = DatabaseConnection()
    db.connect()
    
    print("\n" + "=" * 60)
    print("DATABASE RESET - FULL CLEANUP")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL data!")
    print("This action cannot be undone.\n")
    
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm == 'RESET':
        print("\nDeleting all data...")
        
        # Delete in correct order
        tables = [
            'task_assignments',
            'tasks',
            'group_members',
            'groups',
            'availability',
            'personality_traits',
            'technical_skills',
            'students',
            'system_logs'
        ]
        
        for table in tables:
            db.execute_query(f"DELETE FROM {table}")
            print(f"  ✓ Cleared {table}")
        
        print("\n✓ All data deleted")
        print("\nRun populate_test_data.py to restore sample data")
    else:
        print("\nCancelled - no data was deleted")
    
    print("\n" + "=" * 60)
    
    db.disconnect()

def show_database_stats():
    """Show current database statistics"""
    db = DatabaseConnection()
    db.connect()
    
    print("\n" + "=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    
    stats = {
        'Students': db.fetch_one("SELECT COUNT(*) as count FROM students")['count'],
        'Technical Skills': db.fetch_one("SELECT COUNT(*) as count FROM technical_skills")['count'],
        'Personality Traits': db.fetch_one("SELECT COUNT(*) as count FROM personality_traits")['count'],
        'Availability Slots': db.fetch_one("SELECT COUNT(*) as count FROM availability")['count'],
        'Groups': db.fetch_one("SELECT COUNT(*) as count FROM groups")['count'],
        'Group Members': db.fetch_one("SELECT COUNT(*) as count FROM group_members")['count'],
        'Tasks': db.fetch_one("SELECT COUNT(*) as count FROM tasks")['count'],
        'Task Assignments': db.fetch_one("SELECT COUNT(*) as count FROM task_assignments")['count'],
        'System Logs': db.fetch_one("SELECT COUNT(*) as count FROM system_logs")['count']
    }
    
    print("\nRecord Counts:")
    for table, count in stats.items():
        print(f"  {table:.<30} {count:>6}")
    
    # Check for duplicate group assignments
    duplicate_check = db.fetch_all("""
        SELECT student_id, COUNT(*) as group_count
        FROM group_members
        GROUP BY student_id
        HAVING COUNT(*) > 1
    """)
    
    if duplicate_check:
        print(f"\n⚠️  Warning: Found {len(duplicate_check)} students in multiple groups")
        print("    Run cleanup_all_groups() to fix this")
    else:
        print("\n✓ No duplicate group assignments")
    
    print("\n" + "=" * 60)
    
    db.disconnect()

def main_menu():
    """Interactive menu for database cleanup"""
    while True:
        print("\n" + "=" * 60)
        print("DATABASE CLEANUP UTILITY")
        print("=" * 60)
        print("\n1. Show database statistics")
        print("2. Clean up all groups (keep students)")
        print("3. Remove test students only")
        print("4. Full database reset (delete everything)")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ")
        
        if choice == '1':
            show_database_stats()
        elif choice == '2':
            cleanup_all_groups()
        elif choice == '3':
            cleanup_test_students()
        elif choice == '4':
            reset_database()
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option")

if __name__ == "__main__":
    main_menu()