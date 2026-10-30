from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user') #'user' atau 'admin'
    pertanyaan_keamanan = db.Column(db.String(200))
    jawaban_keamanan = db.Column(db.String(200))
    peminjaman = db.relationship('Peminjaman', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Buku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    penulis = db.Column(db.String(120), nullable=False)
    kategori = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    stok_total = db.Column(db.Integer, default=0)
    stok_tersedia = db.Column(db.Integer, default=0)
    file_pdf = db.Column(db.String(200))
    peminjaman = db.relationship('Peminjaman', backref='buku', lazy=True)
    ratings = db.relationship('Rating', backref='buku', lazy=True)

class Peminjaman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buku_id = db.Column(db.Integer, db.ForeignKey('buku.id'), nullable=False)
    tanggal_pinjam = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_kembali = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    tanggal_dikembalikan = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='dipinjam')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buku_id = db.Column(db.Integer, db.ForeignKey('buku.id'), nullable=False)
    bintang = db.Column(db.Integer, nullable=False)
    ulasan = db.Column(db.Text)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)