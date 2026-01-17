"""
Migration script to add action-feedback loop fields to Decision model
Simplified version - uses direct SQLAlchemy without Flask app
"""
import sqlite3
import os

def migrate_action_feedback_fields():
    """Add action-feedback loop columns and backfill historical data"""
    
    # Path to database
    db_path = os.path.join(os.path.dirname(__file__), 'data', 'agridecision.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("   Please ensure the backend has been run at least once to create the database.")
        return
    
    print("🔄 Starting Action-Feedback Loop migration...")
    print(f"   Database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n📝 Adding new columns...")
        
        # Add advice_status column
        try:
            cursor.execute("ALTER TABLE decisions ADD COLUMN advice_status VARCHAR(20) DEFAULT 'pending'")
            print("✅ Added advice_status column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  advice_status column already exists")
            else:
                raise
        
        # Add actual_action column
        try:
            cursor.execute("ALTER TABLE decisions ADD COLUMN actual_action VARCHAR(30)")
            print("✅ Added actual_action column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  actual_action column already exists")
            else:
                raise
        
        # Add deviation_reason column
        try:
            cursor.execute("ALTER TABLE decisions ADD COLUMN deviation_reason TEXT")
            print("✅ Added deviation_reason column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  deviation_reason column already exists")
            else:
                raise
        
        # Add action_recorded_at column
        try:
            cursor.execute("ALTER TABLE decisions ADD COLUMN action_recorded_at DATETIME")
            print("✅ Added action_recorded_at column")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("⚠️  action_recorded_at column already exists")
            else:
                raise
        
        # Commit column additions
        conn.commit()
        
        # Backfill historical data
        print("\n📊 Backfilling historical data...")
        
        # Set all existing decisions with NULL advice_status to 'pending'
        cursor.execute("""
            UPDATE decisions 
            SET advice_status = 'pending' 
            WHERE advice_status IS NULL
        """)
        
        pending_count = cursor.rowcount
        conn.commit()
        
        print(f"✅ Set {pending_count} historical decisions to 'pending' status")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        
        cursor.execute("SELECT COUNT(*) FROM decisions")
        total_decisions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM decisions WHERE advice_status = 'pending'")
        pending_decisions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM decisions WHERE advice_status = 'followed'")
        followed_decisions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM decisions WHERE advice_status = 'ignored'")
        ignored_decisions = cursor.fetchone()[0]
        
        print(f"   Total decisions: {total_decisions}")
        print(f"   Pending: {pending_decisions}")
        print(f"   Followed: {followed_decisions}")
        print(f"   Ignored: {ignored_decisions}")
        
        # Close connection
        conn.close()
        
        print("\n✨ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart the backend server (Ctrl+C and run 'python app.py' again)")
        print("   2. The new action-feedback loop fields are now available")
        print("   3. Farmers can record their actions via the API")
        print("   4. Advanced analytics will become available as data is collected")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

if __name__ == '__main__':
    migrate_action_feedback_fields()
