from app import app
from models import User

with app.app_context():
    semua_user = User.query.all()
    print("\n=== DAFTAR USER ===")
    for u in semua_user:
        print(f"ID: {u.id} | Username: {u.username} | Role: {u.role}")
        print("====================\n")