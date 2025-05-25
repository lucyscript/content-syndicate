#!/usr/bin/env python3
"""Fix subscription tier values in database"""

from app.database import SessionLocal
from sqlalchemy import text

def fix_subscription_tiers():
    db = SessionLocal()
    try:
        # Update lowercase to uppercase
        result = db.execute(text("UPDATE users SET subscription_tier = 'STARTER' WHERE subscription_tier = 'starter'"))
        print(f"Updated {result.rowcount} rows from 'starter' to 'STARTER'")
        
        result = db.execute(text("UPDATE users SET subscription_tier = 'PROFESSIONAL' WHERE subscription_tier = 'professional'"))
        print(f"Updated {result.rowcount} rows from 'professional' to 'PROFESSIONAL'")
        
        result = db.execute(text("UPDATE users SET subscription_tier = 'ENTERPRISE' WHERE subscription_tier = 'enterprise'"))
        print(f"Updated {result.rowcount} rows from 'enterprise' to 'ENTERPRISE'")
        
        db.commit()
        print("✅ Successfully fixed subscription tier values")
        
        # Verify the fix
        result = db.execute(text("SELECT DISTINCT subscription_tier FROM users")).fetchall()
        print(f"Current subscription_tier values: {[row[0] for row in result]}")
        
    except Exception as e:
        print(f"❌ Error fixing subscription tiers: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_subscription_tiers()
