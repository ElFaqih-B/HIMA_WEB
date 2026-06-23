from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, jsonify
from database import get_db_connection
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from utils.activity_logger import log_activity

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

admin_bp = Blueprint('admin', __name__)

# ==========================================
# DASHBOARD UTAMA
# ==========================================
@admin_bp.route('/admin/dashboard')
def dashboard():
    if not session.get('sudah_login'):
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM berita")
    total_berita = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM program_kerja")
    total_proker = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM struktur")
    total_pengurus = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM program_kerja WHERE status = 'ongoing'")
    proker_ongoing = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as total FROM visitor_logs")
    total_visitor = cursor.fetchone()['total']

    # Ambil Log Aktivitas Admin
    cursor.execute("""
        SELECT a.id, a.aktivitas as judul, a.created_at, ad.username as admin_id 
        FROM activity_logs a
        LEFT JOIN admin ad ON a.admin_id = ad.id
        ORDER BY a.created_at DESC LIMIT 10
    """)
    recent_logs = cursor.fetchall()

    # Ambil Log Pengunjung Publik
    cursor.execute("SELECT ip_address, halaman, visited_at FROM visitor_logs ORDER BY visited_at DESC LIMIT 10")
    visitor_logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin/dashboard.html', 
                           total_berita=total_berita, 
                           total_proker=total_proker,
                           total_pengurus=total_pengurus,
                           proker_ongoing=proker_ongoing,
                           total_visitor=total_visitor,
                           recent_logs=recent_logs,
                           visitor_logs=visitor_logs)

# ==========================================
# MANAJEMEN PUBLIKASI (BERITA)
# ==========================================
@admin_bp.route('/admin/berita')
def admin_berita():
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM berita ORDER BY created_at DESC")
    berita_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/berita.html', berita_list=berita_list)

@admin_bp.route('/admin/berita/tambah', methods=['GET', 'POST'])
def tambah_berita():
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        return render_template('admin/tambah_berita.html')
        
    judul = request.form['judul']
    konten = request.form['konten']
    foto_file = request.files.get('gambar_berita')
    foto_url = None
    
    if foto_file and foto_file.filename != '' and allowed_file(foto_file.filename):
        filename = secure_filename(foto_file.filename)
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
        foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        foto_file.save(foto_path)
        foto_url = f"/static/uploads/{unique_filename}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO berita (judul, konten, gambar_url) VALUES (%s, %s, %s)",
        (judul, konten, foto_url)
    )
    conn.commit()
    cursor.close()
    conn.close()

    log_activity(f"Menerbitkan publikasi: {judul}")
    buat_notifikasi('Publikasi Baru', f'Berhasil menerbitkan "{judul}"', 'success')
    return redirect(url_for('admin.admin_berita'))

@admin_bp.route('/admin/berita/edit/<int:id>', methods=['GET'])
def edit_berita_view(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM berita WHERE id = %s", (id,))
    berita = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/edit_berita.html', berita=berita)

@admin_bp.route('/update_berita/<int:id>', methods=['POST'])
def update_berita(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    judul = request.form['judul']
    konten = request.form['konten']
    foto_file = request.files.get('gambar_berita')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if foto_file and foto_file.filename != '' and allowed_file(foto_file.filename):
        filename = secure_filename(foto_file.filename)
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
        foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        foto_file.save(foto_path)
        foto_url = f"/static/uploads/{unique_filename}"
        cursor.execute("UPDATE berita SET judul=%s, konten=%s, gambar_url=%s WHERE id=%s", (judul, konten, foto_url, id))
    else:
        cursor.execute("UPDATE berita SET judul=%s, konten=%s WHERE id=%s", (judul, konten, id))
        
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(f"Memperbarui publikasi ID {id}")
    return redirect(url_for('admin.admin_berita'))

@admin_bp.route('/delete_berita/<int:id>', methods=['POST'])
def delete_berita(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM berita WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(f"Menghapus publikasi ID {id}")
    return redirect(url_for('admin.admin_berita'))

# ==========================================
# MANAJEMEN PROGRAM KERJA
# ==========================================
@admin_bp.route('/admin/proker')
def admin_proker():
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM program_kerja ORDER BY id DESC")
    proker_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/proker.html', proker_list=proker_list)

@admin_bp.route('/admin/proker/tambah', methods=['GET', 'POST'])
def tambah_proker():
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    
    if request.method == 'GET':
        return render_template('admin/tambah_proker.html')
        
    nama = request.form['nama_proker']
    deskripsi = request.form['deskripsi']
    status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO program_kerja (nama_program, deskripsi, status) VALUES (%s, %s, %s)",
        (nama, deskripsi, status)
    )
    conn.commit()
    cursor.close()
    conn.close()

    log_activity(f"Menambah program kerja: {nama}")
    buat_notifikasi('Program Kerja', f'Berhasil menambah "{nama}"', 'success')
    return redirect(url_for('admin.admin_proker'))

@admin_bp.route('/admin/proker/edit/<int:id>', methods=['GET'])
def edit_proker_view(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM program_kerja WHERE id = %s", (id,))
    proker = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/edit_proker.html', proker=proker)

@admin_bp.route('/update_proker/<int:id>', methods=['POST'])
def update_proker(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    nama = request.form['nama_proker']
    deskripsi = request.form['deskripsi']
    status = request.form['status']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE program_kerja SET nama_program=%s, deskripsi=%s, status=%s WHERE id=%s", (nama, deskripsi, status, id))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(f"Update program kerja ID {id}")
    return redirect(url_for('admin.admin_proker'))

@admin_bp.route('/delete_proker/<int:id>', methods=['POST'])
def delete_proker(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM program_kerja WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(f"Hapus program kerja ID {id}")
    return redirect(url_for('admin.admin_proker'))

# ==========================================
# MANAJEMEN STRUKTUR (PENGURUS)
# ==========================================
@admin_bp.route('/admin/struktur')
def admin_struktur():
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM struktur ORDER BY id DESC")
    struktur_list = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/struktur.html', struktur_list=struktur_list)

@admin_bp.route('/admin/struktur/tambah', methods=['GET', 'POST'])
def tambah_struktur():
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template('admin/tambah_struktur.html')
        
    nama = request.form['nama']
    jabatan = request.form['jabatan']
    divisi = request.form['divisi']
    periode = request.form['periode'] 
    foto_url = None 
    
    foto_file = request.files.get('foto_pengurus')
    
    if foto_file and foto_file.filename != '' and allowed_file(foto_file.filename):
        filename = secure_filename(foto_file.filename)
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
        foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        foto_file.save(foto_path)
        foto_url = f"/static/uploads/{unique_filename}"
    # Diambil dari form dropdown
    
    # ... (proses simpan foto) ...
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO struktur (nama, jabatan, divisi, foto_url, periode) VALUES (%s, %s, %s, %s, %s)",
        (nama, jabatan, divisi, foto_url, periode)
    )
    conn.commit()
    cursor.close()
    conn.close()

    log_activity(f"Menambah pengurus: {nama}")
    buat_notifikasi('Kepengurusan', f'Berhasil menambah "{nama}"', 'success')
    return redirect(url_for('admin.admin_struktur'))

@admin_bp.route('/admin/struktur/edit/<int:id>', methods=['GET'])
def edit_struktur_view(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM struktur WHERE id = %s", (id,))
    person = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin/edit_struktur.html', person=person)

@admin_bp.route('/update_struktur/<int:id>', methods=['POST'])
def update_struktur(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    nama = request.form['nama']
    jabatan = request.form['jabatan']
    divisi = request.form['divisi']
    periode = request.form.get('periode', '2025/2026')
    
    foto_file = request.files.get('foto_pengurus')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if foto_file and foto_file.filename != '' and allowed_file(foto_file.filename):
        filename = secure_filename(foto_file.filename)
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
        foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        foto_file.save(foto_path)
        foto_url = f"/static/uploads/{unique_filename}"
        
        cursor.execute("UPDATE struktur SET nama=%s, jabatan=%s, divisi=%s, foto_url=%s, periode=%s WHERE id=%s", (nama, jabatan, divisi, foto_url, periode, id))
    else:
        cursor.execute("UPDATE struktur SET nama=%s, jabatan=%s, divisi=%s, periode=%s WHERE id=%s", (nama, jabatan, divisi, periode, id))
        
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(f"Update pengurus ID {id}")
    return redirect(url_for('admin.admin_struktur'))

@admin_bp.route('/delete_struktur/<int:id>', methods=['POST'])
def delete_struktur(id):
    if not session.get('sudah_login'): return redirect(url_for('auth.login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM struktur WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    log_activity(f"Hapus pengurus ID {id}")
    return redirect(url_for('admin.admin_struktur'))

# ==========================================
# GLOBAL SEARCH API & NOTIFIKASI
# ==========================================
@admin_bp.route('/admin/api/search')
def api_search():
    if not session.get('sudah_login'): return jsonify([])
    
    query = request.args.get('q', '').lower()
    if len(query) < 2: return jsonify([])
    
    results = []
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, judul FROM berita WHERE LOWER(judul) LIKE %s LIMIT 3", ('%' + query + '%',))
    for row in cursor.fetchall():
        results.append({'title': row['judul'], 'type': 'Publikasi', 'url': f'/admin/berita/edit/{row["id"]}', 'icon': '📝'})
        
    cursor.execute("SELECT id, nama_program FROM program_kerja WHERE LOWER(nama_program) LIKE %s LIMIT 3", ('%' + query + '%',))
    for row in cursor.fetchall():
        results.append({'title': row['nama_program'], 'type': 'Program Kerja', 'url': f'/admin/proker/edit/{row["id"]}', 'icon': '🎯'})
        
    cursor.execute("SELECT id, nama, jabatan FROM struktur WHERE LOWER(nama) LIKE %s LIMIT 3", ('%' + query + '%',))
    for row in cursor.fetchall():
        results.append({'title': row['nama'], 'type': f'Pengurus - {row["jabatan"]}', 'url': f'/admin/struktur/edit/{row["id"]}', 'icon': '👤'})
        
    cursor.close()
    conn.close()
    return jsonify(results)

def buat_notifikasi(judul, pesan, tipe='info'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notifikasi (judul, pesan, tipe) VALUES (%s, %s, %s)", (judul, pesan, tipe))
    conn.commit()
    cursor.close()
    conn.close()

@admin_bp.route('/admin/api/notifikasi', methods=['GET'])
def api_notifikasi():
    if not session.get('sudah_login'): return jsonify([])
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM notifikasi WHERE is_read = 0 ORDER BY created_at DESC LIMIT 10")
    notifs = cursor.fetchall()
    cursor.close()
    conn.close()
    for n in notifs:
        if n['created_at']:
            n['waktu'] = n['created_at'].strftime('%d %b %H:%M')
    return jsonify(notifs)

@admin_bp.route('/admin/api/notifikasi/read/<int:id>', methods=['POST'])
def mark_read_notifikasi(id):
    if not session.get('sudah_login'): return jsonify({'status': 'error'})
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifikasi SET is_read = 1 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'ok'})

@admin_bp.route('/admin/pengaturan')
def admin_pengaturan():
    if not session.get('sudah_login'): 
        return redirect(url_for('auth.login'))
    return render_template('admin/pengaturan.html')

@admin_bp.route('/update_hero', methods=['POST'])
def update_hero():
    if not session.get('sudah_login'): 
        return redirect(url_for('auth.login'))
        
    foto_file = request.files.get('gambar_hero')
    if foto_file and foto_file.filename != '' and allowed_file(foto_file.filename):
        filename = secure_filename(foto_file.filename)
        unique_filename = f"{int(datetime.now().timestamp())}_{filename}"
        foto_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        foto_file.save(foto_path)
        foto_url = f"/static/uploads/{unique_filename}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Mengecek apakah config_key hero_image sudah ada di database
        cursor.execute("SELECT * FROM site_config WHERE config_key = 'hero_image'")
        config_exist = cursor.fetchone()
        
        if config_exist:
            cursor.execute("UPDATE site_config SET config_value = %s WHERE config_key = 'hero_image'", (foto_url,))
        else:
            cursor.execute("INSERT INTO site_config (config_key, config_value) VALUES ('hero_image', %s)", (foto_url,))
            
        conn.commit()
        cursor.close()
        conn.close()
        
        # Opsional: Jika kamu ingin mencatat aktivitas ini (memerlukan import log_activity dari utils)
        try:
            log_activity("Memperbarui gambar background landing page")
        except:
            pass
            
    return redirect(url_for('admin.admin_pengaturan'))