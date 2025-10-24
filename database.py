import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DATABASE_FILE = "clausewise.db"

# Auto-remove database at startup
if os.path.exists(DATABASE_FILE):
    os.remove(DATABASE_FILE)

def init_database():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            analysis_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents (id)
        )
    ''')
    
    # Create users table for authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_document(filename: str, content: str) -> int:
    """Save a document to the database and return its ID"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO documents (filename, content) VALUES (?, ?)",
        (filename, content)
    )
    
    document_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return document_id

def save_analysis(document_id: int, analysis_data: Dict[Any, Any]) -> int:
    """Save analysis results to the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Convert analysis data to JSON string
    analysis_json = json.dumps(analysis_data, default=str)
    
    cursor.execute(
        "INSERT INTO analysis (document_id, analysis_data) VALUES (?, ?)",
        (document_id, analysis_json)
    )
    
    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return analysis_id

def get_documents() -> List[Dict[str, Any]]:
    """Retrieve all documents from the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT d.id, d.filename, d.created_at, a.id as analysis_id
        FROM documents d
        LEFT JOIN analysis a ON d.id = a.document_id
        ORDER BY d.created_at DESC
    ''')
    
    documents = []
    for row in cursor.fetchall():
        documents.append({
            'id': row[0],
            'filename': row[1],
            'created_at': datetime.fromisoformat(row[2]),
            'analysis_id': row[3]
        })
    
    conn.close()
    return documents

def get_document_analysis(document_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve analysis results for a specific document"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT analysis_data FROM analysis WHERE document_id = ? ORDER BY created_at DESC LIMIT 1",
        (document_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def save_user(username: str, password_hash: str) -> int:
    """Save a user to the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        raise ValueError("Username already exists")

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user by username"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'username': result[1],
            'password_hash': result[2]
        }
    return None
