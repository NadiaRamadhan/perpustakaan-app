from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE user ADD COLUMN pertanyaan_keamanan VARCHAR(200)"))
            conn.execute(text("ALTER TABLE user ADD COLUMN jawaban_keamanan VARCHAR(200)"))
            conn.commit()
        print("✅ Kolom keamanan berhasil ditambahkan!")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("ℹ️ Kolom sudah ada.")
        else:
            print(f"❌ Error: {e}")