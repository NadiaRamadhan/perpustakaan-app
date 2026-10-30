import os
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app
from models import db, User, Buku, Peminjaman, Rating

# konfigurasi folder upload pdf
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'pdf')
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    # Ambil parameter dari URL (?q=...&kategori=...)
    q = request.args.get('q', '').strip()
    kategori = request.args.get('kategori', '').strip()

    # Query dasar
    query = Buku.query

    # Filter berdasarkan pencarian (judul ATAU penulis)
    if q:
        query = query.filter(
            db.or_(
                Buku.judul.ilike(f'%{q}%'),
                Buku.penulis.ilike(f'%{q}%')
            )
        )

    # Filter berdasarkan kategori
    if kategori:
        query = query.filter(Buku.kategori == kategori)

    buku_list = query.all()

    # Ambil daftar kategori unik untuk dropdown filter
    semua_kategori = db.session.query(Buku.kategori).distinct().all()
    semua_kategori = [k[0] for k in semua_kategori if k[0]]

    return render_template('index.html',
                        buku_list=buku_list,
                        q=q,
                        kategori_terpilih=kategori,
                        semua_kategori=semua_kategori)

@app.route('/buku/<int:buku_id>')
def detail_buku(buku_id):
    buku = Buku.query.get_or_404(buku_id)
    ratings = Rating.query.filter_by(buku_id=buku_id).all()
    rata_rata = sum(r.bintang for r in ratings) / len(ratings) if ratings else 0
    return render_template('book_detail.html', buku=buku, ratings=ratings, rata_rata=rata_rata)

#---------- REGISTER ------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        pertanyaan = request.form['pertanyaan_keamanan']
        jawaban = request.form['jawaban_keamanan'].lower().strip()

        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar!', 'danger')
            return redirect(url_for('register'))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            pertanyaan_keamanan=pertanyaan,
            jawaban_keamanan=generate_password_hash(jawaban)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

#---------- LOGIN ---------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Selamat datang, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau Password salah.', 'danger')
    return render_template('login.html')

#---------- LOGOUT ----------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

#--------- PINJAM BUKU ----------------
@app.route('/pinjam/<int:buku_id>', methods=['POST'])
@login_required
def pinjam_buku(buku_id):
    buku = Buku.query.get_or_404(buku_id)

    if buku.stok_tersedia <= 0:
        flash('Maaf, stok buku habis.', 'danger')
        return redirect(url_for('detail_buku', buku_id=buku_id))

    pinjaman_aktif = Peminjaman.query.filter_by(
        user_id=current_user.id, buku_id=buku_id, status='dipinjam'
    ).first()
    if pinjaman_aktif:
        flash('Anda masih meminjam buku ini.', 'warning')
        return redirect(url_for('detail_buku', buku_id=buku_id))

    peminjaman = Peminjaman(user_id=current_user.id, buku_id=buku_id)
    buku.stok_tersedia -= 1
    db.session.add(peminjaman)
    db.session.commit()
    flash(f'Berhasil meminjam "{buku.judul}".', 'success')
    return redirect(url_for('dashboard'))

#--------- DASHBOARD USER -------------
@app.route('/dashboard')
@login_required
def dashboard():
    peminjaman = Peminjaman.query.filter_by(user_id=current_user.id).order_by(
        Peminjaman.tanggal_pinjam.desc()
    ).all()
    return render_template('dashboard.html', peminjaman=peminjaman)

# ---------- KEMBALIKAN BUKU ----------
@app.route('/kembalikan/<int:peminjaman_id>', methods=['POST'])
@login_required
def kembalikan_buku(peminjaman_id):
    peminjaman = Peminjaman.query.get_or_404(peminjaman_id)

    if peminjaman.user_id != current_user.id:
        flash('Anda tidak berhak mengembalikan buku ini.', 'danger')
        return redirect(url_for('dashboard'))

    peminjaman.status = 'dikembalikan'
    peminjaman.tanggal_dikembalikan = datetime.utcnow()
    peminjaman.buku.stok_tersedia += 1
    db.session.commit()
    flash('Buku berhasil dikembalikan. Silakan beri rating!', 'success')
    return redirect(url_for('beri_rating', buku_id=peminjaman.buku_id))

# ---------- BERI RATING ----------
@app.route('/rating/<int:buku_id>', methods=['GET', 'POST'])
@login_required
def beri_rating(buku_id):
    buku = Buku.query.get_or_404(buku_id)
    if request.method == 'POST':
        bintang = int(request.form['bintang'])
        ulasan = request.form.get('ulasan', '')

        existing = Rating.query.filter_by(user_id=current_user.id, buku_id=buku_id).first()
        if existing:
            existing.bintang = bintang
            existing.ulasan = ulasan
        else:
            rating = Rating(
                user_id=current_user.id,
                buku_id=buku_id,
                bintang=bintang,
                ulasan=ulasan
            )
            db.session.add(rating)

        db.session.commit()
        flash('Terima kasih atas rating Anda!', 'success')
        return redirect(url_for('detail_buku', buku_id=buku_id))
    return render_template('beri_rating.html', buku=buku)

# ---------- ADMIN: TAMBAH BUKU ----------
@app.route('/admin/tambah-buku', methods=['GET', 'POST'])
@login_required
def tambah_buku():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa menambah buku.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        judul = request.form['judul']
        penulis = request.form['penulis']
        kategori = request.form['kategori']
        deskripsi = request.form['deskripsi']
        stok = int(request.form['stok'])

        # Handle upload PDF
        file_pdf_name = None
        file = request.files.get('file_pdf')
        if file and file.filename != '':
            if allowed_file(file.filename):
                # Bikin nama unik: judul + timestamp
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                safe_name = secure_filename(file.filename)
                file_pdf_name = f"{timestamp}_{safe_name}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_pdf_name))
            else:
                flash('Hanya file PDF yang diperbolehkan!', 'danger')
                return redirect(url_for('tambah_buku'))

        buku = Buku(
            judul=judul,
            penulis=penulis,
            kategori=kategori,
            deskripsi=deskripsi,
            stok_total=stok,
            stok_tersedia=stok,
            file_pdf=file_pdf_name
        )
        db.session.add(buku)
        db.session.commit()
        flash('Buku berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))
    return render_template('tambah_buku.html')

    # ---------- CETAK STRUK ----------
@app.route('/struk/<int:peminjaman_id>')
@login_required
def cetak_struk(peminjaman_id):
    peminjaman = Peminjaman.query.get_or_404(peminjaman_id)

    if peminjaman.user_id != current_user.id and current_user.role != 'admin':
        flash('Anda tidak berhak melihat struk ini.', 'danger')
        return redirect(url_for('dashboard'))

    return render_template('struk.html', p=peminjaman)

    # ---------- BACA PDF ----------
@app.route('/baca/<int:buku_id>')
@login_required
def baca_buku(buku_id):
    buku = Buku.query.get_or_404(buku_id)

    if not buku.file_pdf:
        flash('File PDF untuk buku ini belum tersedia.', 'warning')
        return redirect(url_for('detail_buku', buku_id=buku_id))

    return render_template('baca_pdf.html', buku=buku)

    # ---------- ADMIN: HAPUS BUKU ----------
@app.route('/admin/hapus-buku/<int:buku_id>', methods=['POST'])
@login_required
def hapus_buku(buku_id):
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa menghapus buku.', 'danger')
        return redirect(url_for('index'))

    buku = Buku.query.get_or_404(buku_id)

    # Hapus file PDF kalau ada
    if buku.file_pdf:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], buku.file_pdf)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Hapus data terkait
    Rating.query.filter_by(buku_id=buku.id).delete()
    Peminjaman.query.filter_by(buku_id=buku.id).delete()
    db.session.delete(buku)
    db.session.commit()

    flash(f'Buku "{buku.judul}" berhasil dihapus.', 'success')
    return redirect(url_for('index'))

    # ---------- GANTI PASSWORD ----------
@app.route('/ganti-password', methods=['GET', 'POST'])
@login_required
def ganti_password():
    if request.method == 'POST':
        password_lama = request.form['password_lama']
        password_baru = request.form['password_baru']
        konfirmasi = request.form['konfirmasi']

        # Cek password lama
        if not check_password_hash(current_user.password_hash, password_lama):
            flash('Password lama salah!', 'danger')
            return redirect(url_for('ganti_password'))

        # Cek konfirmasi
        if password_baru != konfirmasi:
            flash('Konfirmasi password tidak cocok!', 'danger')
            return redirect(url_for('ganti_password'))

        # Cek panjang minimal
        if len(password_baru) < 4:
            flash('Password baru minimal 4 karakter!', 'danger')
            return redirect(url_for('ganti_password'))

        # Simpan password baru
        current_user.password_hash = generate_password_hash(password_baru)
        db.session.commit()
        flash('Password berhasil diubah!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('ganti_password.html')

# ---------- LUPA PASSWORD: STEP 1 ----------
@app.route('/lupa-password', methods=['GET', 'POST'])
def lupa_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash('Username tidak ditemukan!', 'danger')
            return redirect(url_for('lupa_password'))

        if not user.pertanyaan_keamanan:
            flash('Akun ini tidak punya pertanyaan keamanan. Hubungi admin.', 'warning')
            return redirect(url_for('lupa_password'))

        return redirect(url_for('jawab_keamanan', user_id=user.id))

    return render_template('lupa_password.html')

# ---------- LUPA PASSWORD: STEP 2 ----------
@app.route('/jawab-keamanan/<int:user_id>', methods=['GET', 'POST'])
def jawab_keamanan(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        jawaban = request.form['jawaban'].lower().strip()
        password_baru = request.form['password_baru']
        konfirmasi = request.form['konfirmasi']

        if not check_password_hash(user.jawaban_keamanan, jawaban):
            flash('Jawaban salah!', 'danger')
            return redirect(url_for('jawab_keamanan', user_id=user_id))

        if password_baru != konfirmasi:
            flash('Konfirmasi password tidak cocok!', 'danger')
            return redirect(url_for('jawab_keamanan', user_id=user_id))

        if len(password_baru) < 4:
            flash('Password minimal 4 karakter!', 'danger')
            return redirect(url_for('jawab_keamanan', user_id=user_id))

        user.password_hash = generate_password_hash(password_baru)
        db.session.commit()
        flash('Password berhasil direset! Silakan login dengan password baru.', 'success')
        return redirect(url_for('login'))

    return render_template('jawab_keamanan.html', user=user)

# ---------- ADMIN: DASHBOARD ----------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Akses ditolak. Hanya admin yang bisa masuk.', 'danger')
        return redirect(url_for('index'))

    # Filter status dari URL (?status=dipinjam)
    status_filter = request.args.get('status', '').strip()

    # Query dasar
    query = Peminjaman.query

    if status_filter == 'dipinjam':
        query = query.filter_by(status='dipinjam')
    elif status_filter == 'dikembalikan':
        query = query.filter_by(status='dikembalikan')
    elif status_filter == 'terlambat':
        query = query.filter(
            Peminjaman.status == 'dipinjam',
            Peminjaman.tanggal_kembali < datetime.utcnow()
        )

    semua_peminjaman = query.order_by(Peminjaman.tanggal_pinjam.desc()).all()

    # Statistik ringkas
    total_buku = Buku.query.count()
    total_stok = db.session.query(db.func.sum(Buku.stok_total)).scalar() or 0
    total_user = User.query.filter_by(role='user').count()
    total_pinjam_aktif = Peminjaman.query.filter_by(status='dipinjam').count()
    total_dikembalikan = Peminjaman.query.filter_by(status='dikembalikan').count()

    # ============ DATA UNTUK GRAFIK ============

    # 1. Top 5 buku paling sering dipinjam
    top_buku_query = db.session.query(
        Buku.judul,
        db.func.count(Peminjaman.id).label('total')
    ).join(Peminjaman, Peminjaman.buku_id == Buku.id)\
     .group_by(Buku.id)\
     .order_by(db.func.count(Peminjaman.id).desc())\
     .limit(5).all()

    top_buku_labels = [b[0] for b in top_buku_query]
    top_buku_data = [b[1] for b in top_buku_query]

    # 2. Jumlah buku per kategori
    kategori_query = db.session.query(
        Buku.kategori,
        db.func.count(Buku.id).label('total')
    ).group_by(Buku.kategori).all()

    kategori_labels = [k[0] or 'Tidak Berkategori' for k in kategori_query]
    kategori_data = [k[1] for k in kategori_query]

    # 3. Peminjaman per bulan (6 bulan terakhir)
    from datetime import timedelta
    enam_bulan_lalu = datetime.utcnow() - timedelta(days=180)

    bulan_query = db.session.query(
        db.func.strftime('%Y-%m', Peminjaman.tanggal_pinjam).label('bulan'),
        db.func.count(Peminjaman.id).label('total')
    ).filter(Peminjaman.tanggal_pinjam >= enam_bulan_lalu)\
    .group_by('bulan')\
    .order_by('bulan').all()

    bulan_labels = [b[0] for b in bulan_query]
    bulan_data = [b[1] for b in bulan_query]

    return render_template('admin_dashboard.html',
                        semua_peminjaman=semua_peminjaman,
                        total_buku=total_buku,
                        total_stok=total_stok,
                        total_user=total_user,
                        total_pinjam_aktif=total_pinjam_aktif,
                        total_dikembalikan=total_dikembalikan,
                        status_filter=status_filter,
                        now=datetime.utcnow(),
                        top_buku_labels=top_buku_labels,
                        top_buku_data=top_buku_data,
                        kategori_labels=kategori_labels,
                        kategori_data=kategori_data,
                        bulan_labels=bulan_labels,
                        bulan_data=bulan_data)