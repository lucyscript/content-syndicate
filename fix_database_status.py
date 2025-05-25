#!/usr/bin/env python3
"""
Fix database newsletter status values to match enum definitions
"""
import sqlite3

def fix_newsletter_status():
    """Update all lowercase status values to uppercase to match the enum definition"""
    try:
        conn = sqlite3.connect('contentsyndicate.db')
        cursor = conn.cursor()

        # Check current status values
        cursor.execute('SELECT DISTINCT status FROM newsletters')
        current_statuses = cursor.fetchall()
        print('Current newsletter statuses in database:', current_statuses)

        # Update all lowercase status values to uppercase
        updates = [
            ('DRAFT', 'draft'),
            ('GENERATING', 'generating'), 
            ('READY', 'ready'),
            ('SENT', 'sent'),
            ('FAILED', 'failed')
        ]

        total_updated = 0
        for uppercase, lowercase in updates:
            cursor.execute('UPDATE newsletters SET status = ? WHERE status = ?', (uppercase, lowercase))
            updated_count = cursor.rowcount
            if updated_count > 0:
                print(f'Updated {updated_count} newsletters from "{lowercase}" to "{uppercase}"')
                total_updated += updated_count

        conn.commit()

        # Verify the changes
        cursor.execute('SELECT DISTINCT status FROM newsletters')
        updated_statuses = cursor.fetchall()
        print('Updated newsletter statuses in database:', updated_statuses)

        # Count total newsletters
        cursor.execute('SELECT COUNT(*) FROM newsletters')
        total_newsletters = cursor.fetchone()[0]
        print(f'Total newsletters in database: {total_newsletters}')
        print(f'Total status values updated: {total_updated}')

        conn.close()
        print('Database status values updated successfully!')
        return True

    except Exception as e:
        print(f'Error updating database: {e}')
        return False

if __name__ == '__main__':
    fix_newsletter_status()
