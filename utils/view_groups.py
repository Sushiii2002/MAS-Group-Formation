from db_connection import DatabaseConnection

def view_formed_groups():
    db = DatabaseConnection()
    db.connect()
    
    query = """
    SELECT g.id, g.group_name, g.compatibility_score,
           s.first_name, s.last_name, s.gwa, gm.role
    FROM groups g
    JOIN group_members gm ON g.id = gm.group_id
    JOIN students s ON gm.student_id = s.id
    ORDER BY g.id, gm.role DESC, s.last_name
    """
    
    results = db.fetch_all(query)
    
    current_group = None
    print("\n" + "=" * 60)
    print("FORMED GROUPS")
    print("=" * 60)
    
    for row in results:
        if current_group != row['group_name']:
            current_group = row['group_name']
            print(f"\n{row['group_name']} (Compatibility: {row['compatibility_score']:.3f})")
        
        role_marker = "👑" if row['role'] == 'Leader' else "  "
        print(f"  {role_marker} {row['first_name']} {row['last_name']} - "
              f"GWA: {row['gwa']} ({row['role']})")
    
    print("\n" + "=" * 60)
    db.disconnect()

if __name__ == "__main__":
    view_formed_groups()