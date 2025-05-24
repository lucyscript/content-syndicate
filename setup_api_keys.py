#!/usr/bin/env python3
"""
ContentSyndicate Setup Guide
Interactive setup script for API keys and configuration
"""

import os
from pathlib import Path

def setup_api_keys():
    """Interactive API key setup"""
    print("🚀 ContentSyndicate API Key Setup")
    print("=" * 50)
    
    env_file = Path(".env")
    current_env = {}
    
    # Read current .env file
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    current_env[key] = value
    
    # API key prompts
    api_keys = {
        'GEMINI_API_KEY': {
            'name': 'Google Gemini API',
            'url': 'https://makersuite.google.com/app/apikey',
            'description': 'Required for AI content generation',
            'priority': 1
        },
        'NEWS_API_KEY': {
            'name': 'NewsAPI',
            'url': 'https://newsapi.org/register',
            'description': 'Required for news content aggregation',
            'priority': 1
        },
        'REDDIT_CLIENT_ID': {
            'name': 'Reddit API Client ID',
            'url': 'https://www.reddit.com/prefs/apps/',
            'description': 'Optional: For Reddit content aggregation',
            'priority': 2
        },
        'REDDIT_CLIENT_SECRET': {
            'name': 'Reddit API Client Secret',
            'url': 'https://www.reddit.com/prefs/apps/',
            'description': 'Optional: For Reddit content aggregation',
            'priority': 2
        },
        'SENDGRID_API_KEY': {
            'name': 'SendGrid API',
            'url': 'https://app.sendgrid.com/settings/api_keys',
            'description': 'Optional: For email newsletter distribution',
            'priority': 3
        }
    }
    
    updated_keys = {}
    
    for key, info in api_keys.items():
        current_value = current_env.get(key, '')
        
        print(f"\n📝 {info['name']} (Priority {info['priority']})")
        print(f"   {info['description']}")
        print(f"   Get your key at: {info['url']}")
        
        if current_value and not current_value.startswith('your_'):
            print(f"   Current value: {current_value[:10]}...")
            update = input(f"   Update this key? (y/N): ").lower().strip()
            if update != 'y':
                updated_keys[key] = current_value
                continue
        
        new_value = input(f"   Enter your {info['name']} (or press Enter to skip): ").strip()
        if new_value:
            updated_keys[key] = new_value
        elif current_value:
            updated_keys[key] = current_value
    
    # Update .env file
    if updated_keys:
        print(f"\n💾 Updating .env file...")
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        with open(env_file, 'w') as f:
            for line in lines:
                written = False
                for key, value in updated_keys.items():
                    if line.startswith(f"{key}=") or line.startswith(f"# {key}="):
                        f.write(f"{key}={value}\n")
                        written = True
                        break
                if not written:
                    f.write(line)
            
            # Add new keys that weren't in the original file
            existing_keys = set()
            for line in lines:
                if '=' in line and not line.strip().startswith('#'):
                    key = line.split('=')[0].strip()
                    existing_keys.add(key)
            
            for key, value in updated_keys.items():
                if key not in existing_keys:
                    f.write(f"{key}={value}\n")
        
        print("✅ Environment file updated!")
    
    print(f"\n🎉 Setup complete!")
    print(f"📁 Configuration saved to: {env_file.absolute()}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Restart the backend server: python start_server.py")
    print(f"   2. Open the frontend: http://localhost:3000")
    print(f"   3. Test newsletter generation!")

if __name__ == "__main__":
    setup_api_keys()
