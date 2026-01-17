"""
Recreate regional_benchmarks table with correct schema
"""
from app import app
from models.base import db
from models.analytics import RegionalBenchmarks, CropSpecificDefaults
from sqlalchemy import inspect

with app.app_context():
    print("Checking regional_benchmarks table schema...")
    
    # Check if table exists
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'regional_benchmarks' in tables:
        print("✅ Table exists, checking columns...")
        cols = inspector.get_columns('regional_benchmarks')
        print("Current columns:")
        for c in cols:
            print(f"  - {c['name']}: {c['type']}")
        
        # Drop and recreate
        print("\n🔄 Dropping and recreating table...")
        db.drop_all(tables=[RegionalBenchmarks.__table__])
        db.create_all(tables=[RegionalBenchmarks.__table__])
        
        # Verify
        cols_after = inspector.get_columns('regional_benchmarks')
        print("\n✅ New columns:")
        for c in cols_after:
            print(f"  - {c['name']}: {c['type']}")
    else:
        print("❌ Table doesn't exist, creating...")
        db.create_all(tables=[RegionalBenchmarks.__table__])
        print("✅ Table created")
