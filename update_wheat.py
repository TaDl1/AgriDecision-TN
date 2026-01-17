import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app
from models.base import db
from models.crop import Crop

app = create_app()
with app.app_context():
    wheat = Crop.query.filter_by(name='Wheat').first()
    if wheat:
        wheat.category = 'legume'
        db.session.commit()
        print("Wheat moved to legume")
    else:
        print("Wheat not found")
