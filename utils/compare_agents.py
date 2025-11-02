from db_connection import DatabaseConnection

def compare_results():
    db = DatabaseConnection()
    db.connect()
    
    # Simple agent results
    simple_query = """
    SELECT AVG(compatibility_score) as avg_score
    FROM groups
    WHERE group_name LIKE 'Group%'
    """
    simple_result = db.fetch_one(simple_query)
    
    # GA agent results
    ga_query = """
    SELECT AVG(compatibility_score) as avg_score
    FROM groups
    WHERE group_name LIKE 'GA Group%'
    """
    ga_result = db.fetch_one(ga_query)
    
    print("\n" + "=" * 60)
    print("AGENT COMPARISON")
    print("=" * 60)
    print(f"Simple Agent Average Compatibility: {simple_result['avg_score']:.3f}")
    print(f"GA Agent Average Compatibility:     {ga_result['avg_score']:.3f}")
    
    improvement = ((ga_result['avg_score'] - simple_result['avg_score']) / 
                   simple_result['avg_score'] * 100)
    print(f"\nImprovement: {improvement:+.2f}%")
    print("=" * 60 + "\n")
    
    db.disconnect()

if __name__ == "__main__":
    compare_results()