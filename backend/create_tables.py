"""
Create missing database tables
"""
from app import app
from models.base import db
from models.analytics import RegionalBenchmarks, CropSpecificDefaults

with app.app_context():
    print("Creating missing database tables...")
    db.create_all()
    print("✅ Database tables created successfully!")
    
    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\n📋 Available tables: {', '.join(tables)}")
    
    if 'regional_benchmarks' in tables:
        print("✅ regional_benchmarks table exists")
    else:
        print("❌ regional_benchmarks table still missing")
