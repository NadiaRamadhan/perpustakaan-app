from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE buku ADD COLUMN file_pdf VARCHAR(200)"))
            conn.commit()
        print("✅ kolom 'file_pdf' berhasil ditambahkan ke tabel buku!")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("❗kolom 'file_pdf' sudah ada, tidak perlu ditambah lagi.")
        else:
            print(f"❌ Error: {e}")