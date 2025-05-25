#!/usr/bin/env python3
import sys
import os
sys.path.append('app')
from app.database import SessionLocal
from app.models import User, SubscriptionTier
from app.auth import get_password_hash

# Create a test user
db = SessionLocal()
try:
    # Check if test user exists
    test_user = db.query(User).filter(User.email == 'test@example.com').first()
    if not test_user:        test_user = User(
            email='test@example.com',
            full_name='Test User',
            hashed_password=get_password_hash('password123'),
            is_active=True,
            subscription_tier=SubscriptionTier.STARTER
        )
        db.add(test_user)
        db.commit()
        print('✅ Test user created: test@example.com / password123')
    else:
        print('✅ Test user already exists: test@example.com / password123')
    
    print(f'User ID: {test_user.id}')
    print(f'Active: {test_user.is_active}')
    print(f'Subscription: {test_user.subscription_tier}')
finally:
    db.close()
