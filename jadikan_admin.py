from app import app
from models import db, User

with app.app_context():
    #ganti usnm dg akun yg mau dijadikan admin
    user = User.query.filter_by(username='senja').first()
    if user:
        user.role = 'admin'
        db.session.commit()
        print(f"✅ User '{user.username}' sekarang jadi admin!")
    else:
        print("❌ User tidak ditemukan. Cek lagi!.")