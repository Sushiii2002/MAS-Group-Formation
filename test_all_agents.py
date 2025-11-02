from agents.matcher_agent_ga import MatcherAgentGA
from agents.coordinator_agent import CoordinatorAgent
from utils.db_connection import DatabaseConnection

def test_full_system():
    print("\n" + "=" * 70)
    print("FULL SYSTEM TEST")
    print("=" * 70)
    
    # Clear old data
    print("\n1. Clearing old groups...")
    db = DatabaseConnection()
    db.connect()
    db.execute_query("DELETE FROM task_assignments")
    db.execute_query("DELETE FROM tasks")
    db.execute_query("DELETE FROM group_members")
    db.execute_query("DELETE FROM groups")
    db.disconnect()
    print("✓ Database cleared")
    
    # Run matcher
    print("\n2. Running Matcher Agent (GA)...")
    matcher = MatcherAgentGA()
    if matcher.run(target_group_size=4):
        print("✓ Groups formed successfully")
    else:
        print("✗ Matcher failed")
        return
    
    # Run coordinator
    print("\n3. Running Coordinator Agent...")
    coordinator = CoordinatorAgent()
    if coordinator.run(create_tasks=True):
        print("✓ Tasks allocated successfully")
    else:
        print("✗ Coordinator failed")
        return
    
    print("\n" + "=" * 70)
    print("✓ FULL SYSTEM TEST COMPLETED")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    test_full_system()