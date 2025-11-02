# Quick script to clear groups: utils/clear_groups.py
from db_connection import DatabaseConnection

db = DatabaseConnection()
db.connect()
db.execute_query("DELETE FROM group_members")
db.execute_query("DELETE FROM groups")
print("✓ Cleared all groups")
db.disconnect()