#!/usr/bin/env python3
import sys
import os
sys.path.append('app')
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
try:
    # Update test user password
    test_user = db.query(User).filter(User.email == 'test@example.com').first()
    if test_user:
        test_user.hashed_password = get_password_hash('password123')
        db.commit()
        print('✅ Test user password updated')
        print(f'Email: {test_user.email}')
        print(f'Active: {test_user.is_active}')
    else:
        print('❌ Test user not found')
finally:
    db.close()
