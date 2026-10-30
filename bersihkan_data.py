from app import app
from models import db, Buku, Peminjaman, Rating

with app.app_context():
    Rating.query.delete()
    Peminjaman.query.delete()
    jumlah = Buku.query.count()
    Buku.query.delete()
    db.session.commit()
    print(f"✅ {jumlah} buku dummy dihapus.")