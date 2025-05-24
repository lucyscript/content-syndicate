"""
Database migration utilities for ContentSyndicate
Simple migration system for database schema changes
"""

import os
import logging
from datetime import datetime
from sqlalchemy import text
from .database import engine, get_db, create_tables
from .models import Base

logger = logging.getLogger(__name__)

class MigrationManager:
    """Simple migration management"""
    
    def __init__(self):
        self.migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
        os.makedirs(self.migrations_dir, exist_ok=True)
    
    def create_migration_table(self):
        """Create migrations tracking table"""
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """))
            conn.commit()
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT name FROM migrations ORDER BY applied_at"))
                return [row[0] for row in result]
        except:
            return []
    
    def apply_migration(self, migration_name: str, sql: str):
        """Apply a migration"""
        with engine.connect() as conn:
            try:
                # Split SQL into individual statements and execute them
                statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
                
                for statement in statements:
                    if statement:
                        conn.execute(text(statement))
                
                # Record migration as applied
                conn.execute(
                    text("INSERT INTO migrations (name) VALUES (:name)"),
                    {"name": migration_name}
                )
                conn.commit()
                logger.info(f"Applied migration: {migration_name}")
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to apply migration {migration_name}: {e}")
                raise
    
    def run_migrations(self):
        """Run all pending migrations"""
        self.create_migration_table()
        applied = self.get_applied_migrations()        # Define migrations
        migrations = [
            {
                "name": "001_initial_schema",
                "sql": "-- Initial schema created by SQLAlchemy models"
            },
            {
                "name": "002_add_indexes",
                "sql": """
                    CREATE INDEX IF NOT EXISTS idx_newsletters_user_id ON newsletters(user_id);
                    CREATE INDEX IF NOT EXISTS idx_newsletters_status ON newsletters(status);
                    CREATE INDEX IF NOT EXISTS idx_newsletters_created_at ON newsletters(created_at);
                    CREATE INDEX IF NOT EXISTS idx_subscribers_user_id ON subscribers(user_id);
                    CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email);
                    CREATE INDEX IF NOT EXISTS idx_subscribers_active ON subscribers(is_active);
                    CREATE INDEX IF NOT EXISTS idx_content_sources_user_id ON content_sources(user_id);
                    CREATE INDEX IF NOT EXISTS idx_analytics_newsletter_id ON newsletter_analytics(newsletter_id);
                """
            },
            {
                "name": "003_add_newsletter_fields",
                "sql": """
                    ALTER TABLE newsletters ADD COLUMN subject_line VARCHAR(255);
                    ALTER TABLE newsletters ADD COLUMN content_sources JSON;
                    ALTER TABLE newsletters ADD COLUMN target_audience VARCHAR(500);
                    ALTER TABLE newsletters ADD COLUMN scheduled_for TIMESTAMP;
                    CREATE INDEX IF NOT EXISTS idx_newsletters_scheduled_for ON newsletters(scheduled_for);
                    CREATE INDEX IF NOT EXISTS idx_newsletters_subject_line ON newsletters(subject_line);
                """
            }
        ]
        
        for migration in migrations:
            if migration["name"] not in applied:
                try:
                    self.apply_migration(migration["name"], migration["sql"])
                except Exception as e:
                    logger.error(f"Migration {migration['name']} failed: {e}")
                    # Continue with other migrations
                    continue

def init_database():
    """Initialize database with tables and migrations"""
    logger.info("Initializing database...")
    
    # Create all tables from models
    create_tables()
    
    # Run migrations
    migration_manager = MigrationManager()
    migration_manager.run_migrations()
    
    logger.info("Database initialization complete")

def reset_database():
    """Reset database (WARNING: Deletes all data)"""
    logger.warning("Resetting database - all data will be lost!")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    
    # Recreate tables
    init_database()
    
    logger.info("Database reset complete")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_database()
        elif command == "reset":
            confirm = input("This will delete all data. Type 'YES' to confirm: ")
            if confirm == "YES":
                reset_database()
            else:
                print("Reset cancelled")
        else:
            print("Available commands: init, reset")
    else:
        print("Usage: python -m app.migrations <command>")
        print("Commands: init, reset")
