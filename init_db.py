from app import app
from models import db, User, Buku, Peminjaman, Rating

with app.app_context():
    db.create_all()
    print("✅ Semua Tabel Berhasil DIbuat!")