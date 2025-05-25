#!/usr/bin/env python3
import sys
import os
sys.path.append('app')
from app.database import SessionLocal
from app.models import User, Newsletter

db = SessionLocal()
try:
    print('📋 All users in database:')
    users = db.query(User).all()
    for user in users:
        print(f'  ID: {user.id}')
        print(f'  Email: {user.email}')
        print(f'  Name: {user.full_name}')
        print(f'  Active: {user.is_active}')
        print(f'  Subscription: {user.subscription_tier}')
        
        # Check newsletters for this user
        newsletters = db.query(Newsletter).filter(Newsletter.user_id == user.id).all()
        print(f'  📰 Newsletters: {len(newsletters)}')
        if newsletters:
            for nl in newsletters[:3]:  # Show first 3
                print(f'    - ID: {nl.id}, Title: {nl.title}, Status: {nl.status}')
        print('-' * 40)
        
finally:
    db.close()
