#!/usr/bin/env python3
"""
Simple validation script to check the distribution module
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from mcp_servers.distribution import DistributionServer
    print("✅ DistributionServer imported successfully")
    
    # Try to create an instance
    server = DistributionServer()
    print("✅ DistributionServer instance created successfully")
    
    # Check if the required methods exist
    methods = ['send_newsletter_email_impl', 'post_to_social_media_impl', 'get_server']
    for method in methods:
        if hasattr(server, method):
            print(f"✅ Method {method} exists")
        else:
            print(f"❌ Method {method} missing")
            
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Now try the factory function
try:
    from mcp_servers.distribution import create_distribution_server
    print("✅ create_distribution_server imported successfully")
    
    server = create_distribution_server()
    print("✅ Factory function works")
    
except ImportError as e:
    print(f"❌ Factory function import error: {e}")
    print("Creating factory function...")
    
    # If the function doesn't exist, let's add it dynamically
    import mcp_servers.distribution as dist_module
    
    def create_distribution_server():
        return dist_module.DistributionServer()
    
    # Add it to the module
    dist_module.create_distribution_server = create_distribution_server
    print("✅ Factory function added dynamically")
    
except Exception as e:
    print(f"❌ Factory function error: {e}")
