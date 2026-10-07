"""
Solar Installation and Maintenance Service Management System
Database Connection and Query Execution Module
Uses mysql-connector-python with real MySQL database.
"""

import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode

# Load environment variables from .env file
load_dotenv()

# ========================================================
# MySQL Database Configuration
# You can set these in .env or update them directly here.
# ========================================================
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_PORT = int(os.getenv("MYSQL_PORT", 3306))
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = os.getenv("MYSQL_DATABASE", "solar_service_db")


def get_db_config(use_database=True):
    """Dynamically load connection parameters from environment or .env."""
    load_dotenv(override=True)
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", 3306))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DATABASE", "solar_service_db")

    config = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "charset": "utf8mb4",
        "use_pure": True
    }
    if use_database:
        config["database"] = database
    return config


def get_db_connection(use_database=True):
    """
    Establish a connection to MySQL Server.
    If use_database is True, connects directly to solar_service_db.
    If False, connects to the server without selecting a database (useful for CREATE DATABASE).
    """
    config = get_db_config(use_database=use_database)
    return mysql.connector.connect(**config)


def test_db_connection():
    """
    Test connection to MySQL server and check if the database exists.
    Returns: (is_connected: bool, message: str, db_exists: bool)
    """
    try:
        conn = get_db_connection(use_database=False)
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s;", (DB_NAME,))
        exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        if exists:
            return True, f"Connected to MySQL successfully. Database '{DB_NAME}' is active.", True
        else:
            return True, f"Connected to MySQL server, but database '{DB_NAME}' is not yet created.", False
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return False, "Access denied: Please verify your MySQL username and password in .env or database.py.", False
        elif err.errno == errorcode.CR_CONN_HOST_ERROR or err.errno == 2003:
            return False, f"Could not connect to MySQL server at {DB_HOST}:{DB_PORT}. Ensure MySQL service is running.", False
        else:
            return False, f"MySQL Error [{err.errno}]: {err.msg}", False
    except Exception as e:
        return False, f"Connection failed: {str(e)}", False


def execute_query(sql, params=None, fetch="all", commit=False):
    """
    Execute a parameterized SQL statement with safe resource cleanup.
    
    Parameters:
        sql (str): SQL statement to execute.
        params (tuple or list): Values for query parameters.
        fetch (str): 'all' for fetchall(), 'one' for fetchone(), None for no fetch.
        commit (bool): True for INSERT/UPDATE/DELETE transactions.
        
    Returns:
        For SELECT: list of dicts (fetch='all') or single dict (fetch='one').
        For INSERT: lastrowid.
        For UPDATE/DELETE: rowcount.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection(use_database=True)
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        
        result = None
        if commit:
            conn.commit()
            if sql.strip().upper().startswith("INSERT"):
                result = cursor.lastrowid
            else:
                result = cursor.rowcount
        else:
            if fetch == "all":
                result = cursor.fetchall()
            elif fetch == "one":
                result = cursor.fetchone()
                
        return result
    except mysql.connector.Error as err:
        if conn and commit:
            conn.rollback()
        # Translate common DBMS errors into student-friendly messages
        if err.errno == errorcode.ER_ROW_IS_REFERENCED_2 or err.errno == 1451:
            raise Exception("Cannot delete or update this record: It is referenced by other records (Foreign Key Constraint).")
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2 or err.errno == 1452:
            raise Exception("Invalid reference ID: The referenced record does not exist in the parent table.")
        elif err.errno == errorcode.ER_DUP_ENTRY or err.errno == 1062:
            raise Exception(f"Duplicate entry error: {err.msg}")
        else:
            raise Exception(f"Database Error: {err.msg} (Code {err.errno})")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def run_sql_script(file_path):
    """
    Executes a multi-statement SQL script file (used for schema.sql and seed.sql).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    conn = get_db_connection(use_database=False)
    cursor = conn.cursor()
    try:
        for statement in sql_content.split(";"):
            cleaned = statement.strip()
            # Filter out comments and empty statements
            non_comment_lines = [
                line for line in cleaned.splitlines() 
                if not line.strip().startswith("--") and line.strip() != ""
            ]
            executable_statement = "\n".join(non_comment_lines).strip()
            if executable_statement:
                cursor.execute(executable_statement)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def initialize_database(schema_path="schema.sql", seed_path="seed.sql"):
    """
    Runs schema and seed files to set up the database and insert initial records.
    """
    run_sql_script(schema_path)
    if seed_path and os.path.exists(seed_path):
        run_sql_script(seed_path)
