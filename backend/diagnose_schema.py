
from app import create_app
from models.base import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    
    tables = ['farmer_analytics', 'regional_benchmarks', 'crop_specific_defaults']
    for table in tables:
        if inspector.has_table(table):
            print(f"Table {table} exists.")
            columns = [c['name'] for c in inspector.get_columns(table)]
            print(f"Columns: {columns}")
        else:
            print(f"Table {table} MISSING!")
