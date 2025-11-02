from db_connection import DatabaseConnection

def view_task_allocations():
    db = DatabaseConnection()
    db.connect()
    
    query = """
    SELECT g.group_name, t.task_name, t.estimated_hours,
           s.first_name, s.last_name, ta.status
    FROM groups g
    JOIN tasks t ON g.id = t.group_id
    JOIN task_assignments ta ON t.id = ta.task_id
    JOIN students s ON ta.student_id = s.id
    ORDER BY g.group_name, t.task_name
    """
    
    results = db.fetch_all(query)
    
    current_group = None
    print("\n" + "=" * 60)
    print("TASK ALLOCATIONS BY GROUP")
    print("=" * 60)
    
    for row in results:
        if current_group != row['group_name']:
            current_group = row['group_name']
            print(f"\n{row['group_name']}:")
        
        print(f"  • {row['task_name']} ({row['estimated_hours']}h)")
        print(f"    → {row['first_name']} {row['last_name']} [{row['status']}]")
    
    print("\n" + "=" * 60)
    db.disconnect()

if __name__ == "__main__":
    view_task_allocations()