import sqlite3
import os

# Determine the absolute path to the database file
# Assuming the script is run from the ContentSyndicate directory
db_path = os.path.join(os.getcwd(), 'contentsyndicate.db')

print(f"Attempting to connect to database at: {db_path}")

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute a query to select all users
    cursor.execute("SELECT id, email, full_name, subscription_tier, is_active, created_at, updated_at FROM users")

    # Fetch all rows from the query result
    users = cursor.fetchall()

    if users:
        print("\nRegistered Users:")
        print("=" * 80)
        print(f"{'ID':<5} | {'Email':<30} | {'Full Name':<25} | {'Subscription':<10} | {'Active':<7} | {'Created At':<20} | {'Updated At':<20}")
        print("-" * 120)
        for user in users:
            user_id, email, full_name, subscription_tier, is_active, created_at, updated_at = user
            print(f"{user_id:<5} | {email:<30} | {full_name:<25} | {subscription_tier:<10} | {str(is_active):<7} | {created_at:<20} | {updated_at:<20}")
    else:
        print("No users found in the database.")

except sqlite3.Error as e:
    print(f"SQLite error: {e}")
    print(f"Please ensure the database file '{db_path}' exists and is a valid SQLite database.")
    print("If the server was just started, the table might not exist yet if no user has been created.")

finally:
    # Close the database connection
    if 'conn' in locals() and conn:
        conn.close()
