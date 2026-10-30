# 📚 Perpustakaan Online

Aplikasi web fullstack untuk manajemen perpustakaan. Dibuat dengan Python Flask dan SQLite.

---

## ✨ Fitur

### Untuk User

- Lihat daftar buku
- Search & filter buku
- Pinjam buku
- Kembalikan buku + beri rating
- Cetak struk peminjaman
- Ganti & reset password
- Baca PDF buku di browser

### Untuk Admin

- Tambah & hapus buku
- Upload PDF buku
- Dashboard admin dengan grafik statistik
- Lihat semua peminjaman user

---

## 🛠️ Teknologi

- **Backend**: Python 3.8+, Flask 3.0
- **Database**: SQLite + SQLAlchemy
- **Frontend**: HTML5, Bootstrap 5, CSS3
- **Grafik**: Chart.js

---

## 🚀 Cara Menjalankan

### 1. Clone repository

git clone https://github.com/NadiaRamadhan/perpustakaan-app.git
cd perpustakaan-app

### 2. Buat virtual environment

python -m venv venv

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

### 3. Install dependencies

pip install -r requirements.txt

### 4. Buat database

python init_db.py

### 5. Jalankan aplikasi

python run.py

Buka browser ke http://127.0.0.1:5000

### Membuat Akun Admin

python jadikan_admin.py

---

## 📁 Struktur Proyek

perpustakaan-app/
├── app.py
├── models.py
├── routes.py
├── run.py
├── init_db.py
├── jadikan_admin.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
├── static/
└── instance/

---

## 👨‍💻 Author

**Nadia**
