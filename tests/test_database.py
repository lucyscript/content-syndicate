#!/usr/bin/env python3
"""
Database Testing Script
Tests database connectivity, schema, and newsletter data persistence
"""

import sys
import os
import sqlite3
from datetime import datetime
import json

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

def test_database_connection():
    """Test if we can connect to the database"""
    print("🔍 Testing database connection...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'contentsyndicate.db')
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_table_schema():
    """Test database schema and table structure"""
    print("\n🔍 Testing database schema...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'contentsyndicate.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if newsletters table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='newsletters'
        """)
        if cursor.fetchone():
            print("✅ Newsletters table exists")
        else:
            print("❌ Newsletters table does not exist!")
            return False
        
        # Get table schema
        cursor.execute("PRAGMA table_info(newsletters)")
        columns = cursor.fetchall()
        print("📋 Newsletter table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check if users table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        if cursor.fetchone():
            print("✅ Users table exists")
        else:
            print("❌ Users table does not exist!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema check failed: {e}")
        return False

def test_newsletter_data():
    """Test existing newsletter data"""
    print("\n🔍 Testing newsletter data...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'contentsyndicate.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count total newsletters
        cursor.execute("SELECT COUNT(*) FROM newsletters")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total newsletters in database: {total_count}")
        
        if total_count > 0:
            # Get all newsletters
            cursor.execute("""
                SELECT id, title, subject_line, status, created_at, user_id 
                FROM newsletters 
                ORDER BY created_at DESC
            """)
            newsletters = cursor.fetchall()
            
            print("📋 Newsletter list:")
            for nl in newsletters:
                print(f"  ID: {nl[0]}, Title: '{nl[1]}', Status: {nl[3]}, User: {nl[5]}, Created: {nl[4]}")
            
            # Check for orphaned newsletters (no user_id)
            cursor.execute("SELECT COUNT(*) FROM newsletters WHERE user_id IS NULL")
            orphaned = cursor.fetchone()[0]
            if orphaned > 0:
                print(f"⚠️  Found {orphaned} newsletters without user_id")
        else:
            print("📭 No newsletters found in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Newsletter data check failed: {e}")
        return False

def test_user_data():
    """Test user data and user-newsletter relationships"""
    print("\n🔍 Testing user data...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'contentsyndicate.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        print(f"👥 Total users in database: {total_users}")
        
        if total_users > 0:
            # Get all users
            cursor.execute("SELECT id, email, is_active FROM users")
            users = cursor.fetchall()
            
            print("👤 Users list:")
            for user in users:
                print(f"  ID: {user[0]}, Email: {user[1]}, Active: {user[2]}")
                
                # Check newsletters for each user
                cursor.execute("SELECT COUNT(*) FROM newsletters WHERE user_id = ?", (user[0],))
                user_newsletters = cursor.fetchone()[0]
                print(f"    Newsletters: {user_newsletters}")
        else:
            print("👥 No users found in database")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ User data check failed: {e}")
        return False

def create_test_newsletter():
    """Create a test newsletter to verify creation works"""
    print("\n🔍 Testing newsletter creation...")
    
    db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'contentsyndicate.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, ensure we have a test user
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_result = cursor.fetchone()
        
        if not user_result:
            print("Creating test user...")
            cursor.execute("""
                INSERT INTO users (email, hashed_password, is_active)
                VALUES (?, ?, ?)
            """, ("test@example.com", "test_hash", True))
            user_id = cursor.lastrowid
        else:
            user_id = user_result[0]
        
        # Create test newsletter
        test_data = {
            'title': f'Test Newsletter {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'subject_line': 'Test Subject',
            'content': 'This is test content',
            'target_audience': 'Test audience',
            'status': 'draft',
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            INSERT INTO newsletters (title, subject_line, content, target_audience, status, user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_data['title'],
            test_data['subject_line'], 
            test_data['content'],
            test_data['target_audience'],
            test_data['status'],
            test_data['user_id'],
            test_data['created_at'],
            test_data['updated_at']
        ))
        
        newsletter_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Test newsletter created with ID: {newsletter_id}")
        print(f"   Title: {test_data['title']}")
        print(f"   User ID: {test_data['user_id']}")
        
        # Verify it was created
        cursor.execute("SELECT * FROM newsletters WHERE id = ?", (newsletter_id,))
        result = cursor.fetchone()
        if result:
            print("✅ Newsletter successfully verified in database")
        else:
            print("❌ Newsletter not found after creation!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Newsletter creation test failed: {e}")
        return False

def main():
    """Run all database tests"""
    print("🚀 Starting Database Tests\n")
    print("="*50)
    
    tests = [
        test_database_connection,
        test_table_schema,
        test_user_data,
        test_newsletter_data,
        create_test_newsletter
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "="*50)
    print(f"🏁 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✅ All database tests passed!")
    else:
        print("❌ Some database tests failed!")
        print("💡 This might explain why newsletters aren't showing up in the frontend")

if __name__ == "__main__":
    main()
