import os
from app import create_app, db
from app.models import seed_data

app = create_app()
with app.app_context():
    db_path = db.engine.url.database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Existing database deleted.")
    db.create_all()
    seed_data(db)
    print("Database reset and seeded.")