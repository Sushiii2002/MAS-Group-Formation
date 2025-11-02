import sqlite3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConnection:
    """
    SQLite database connection manager for the MAS system.
    Much simpler than MySQL - no server needed!
    """
    
    def __init__(self):
        # Database file path
        self.db_path = os.getenv('DB_PATH', 'database/mas_database.db')
        self.connection = None
        
        # Create database folder if it doesn't exist
        os.makedirs('database', exist_ok=True)
    
    def connect(self):
        """Establish connection to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            # This makes rows accessible as dictionaries
            self.connection.row_factory = sqlite3.Row
            print(f"Successfully connected to database: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def initialize_database(self):
        """
        Create all tables from schema.sql file
        Run this once to set up the database
        """
        try:
            schema_path = 'database/schema.sql'
            
            if not os.path.exists(schema_path):
                print(f"Error: {schema_path} not found!")
                return False
            
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            cursor = self.connection.cursor()
            cursor.executescript(schema_sql)
            self.connection.commit()
            cursor.close()
            
            print("✓ Database initialized successfully!")
            return True
            
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """
        Execute INSERT, UPDATE, DELETE queries
        Returns: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            print(f"Query executed successfully. {affected_rows} rows affected.")
            return True
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return False
    
    def fetch_one(self, query, params=None):
        """
        Fetch single row from database
        Returns: Dictionary with column names as keys
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            row = cursor.fetchone()
            cursor.close()
            
            # Convert Row object to dictionary
            if row:
                return dict(row)
            return None
            
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return None
    
    def fetch_all(self, query, params=None):
        """
        Fetch multiple rows from database
        Returns: List of dictionaries
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            cursor.close()
            
            # Convert Row objects to dictionaries
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error fetching data: {e}")
            return []
    
    def insert_and_get_id(self, query, params=None):
        """
        Execute INSERT query and return the auto-generated ID
        Useful for inserting students and getting their ID immediately
        """
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            print(f"Insert successful. New ID: {last_id}")
            return last_id
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            return None
    
    def get_table_info(self, table_name):
        """
        Get information about a table's structure
        Useful for debugging
        """
        query = f"PRAGMA table_info({table_name})"
        return self.fetch_all(query)
    
    def list_tables(self):
        """
        List all tables in database
        """
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = self.fetch_all(query)
        return [table['name'] for table in tables]

# Usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Create database connection
    db = DatabaseConnection()
    
    if db.connect():
        print("\n✓ Connection successful!")
        
        # Initialize database (create tables)
        print("\nInitializing database tables...")
        if db.initialize_database():
            print("✓ Tables created successfully!")
            
            # List all tables
            print("\nTables in database:")
            tables = db.list_tables()
            for i, table in enumerate(tables, 1):
                print(f"  {i}. {table}")
            
            # Test a simple query
            print("\nTesting query...")
            students = db.fetch_all("SELECT * FROM students LIMIT 5")
            print(f"Found {len(students)} students (should be 0 for new database)")
            
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED!")
            print("=" * 60)
        else:
            print("✗ Failed to initialize database")
        
        db.disconnect()
    else:
        print("✗ Connection failed!")