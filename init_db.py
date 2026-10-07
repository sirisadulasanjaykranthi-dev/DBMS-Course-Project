"""
Database Initialization Script for Solar Service Management System
Run this script to create the database, tables, and insert sample seed records.
Usage:
    python init_db.py
"""

import os
import sys
from database import test_db_connection, initialize_database, execute_query, DB_HOST, DB_PORT, DB_USER, DB_NAME

def main():
    print("=" * 60)
    print(" SOLAR INSTALLATION & MAINTENANCE DBMS - DATABASE SETUP ")
    print("=" * 60)
    print(f"Target Host: {DB_HOST}:{DB_PORT}")
    print(f"User:        {DB_USER}")
    print(f"Database:    {DB_NAME}")
    print("-" * 60)

    # 1. Test Connection
    connected, msg, exists = test_db_connection()
    if not connected:
        print("\n[ERROR] Connection failed!")
        print(f"Details: {msg}")
        print("\nPlease check your credentials in '.env' or 'database.py'.")
        print("Example .env format:")
        print("  MYSQL_HOST=localhost")
        print("  MYSQL_USER=root")
        print("  MYSQL_PASSWORD=your_actual_password")
        print("  MYSQL_DATABASE=solar_service_db")
        sys.exit(1)

    print(f"[OK] {msg}")

    # 2. Run Schema and Seed
    print("\nApplying schema.sql (Creating tables with constraints)...")
    try:
        initialize_database("schema.sql", "seed.sql")
        print("[OK] Schema created and seed data inserted successfully!")
    except Exception as e:
        print(f"\n[ERROR] Initialization failed: {e}")
        sys.exit(1)

    # 3. Verify counts in each table
    print("\nVerifying Database Tables & Record Counts:")
    print("-" * 60)
    tables = ["Customer", "Employee", "Equipment", "Installation", "Maintenance", "Payment", "Feedback"]
    for table in tables:
        try:
            res = execute_query(f"SELECT COUNT(*) AS total FROM {table};", fetch="one")
            count = res["total"] if res else 0
            print(f"  * {table:<15} : {count} records")
        except Exception as e:
            print(f"  * {table:<15} : Error ({e})")

    print("-" * 60)
    print("Setup completed successfully! You can now start Flask with: python app.py")
    print("=" * 60)

if __name__ == "__main__":
    main()
