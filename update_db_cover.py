from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE buku ADD COLUMN cover VARCHAR(200)"))
            conn.commit()
            print("kolom cover berhasil ditambahkan")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("kolom cover sudah ada")
        else:
            print(f"Error: {e}")