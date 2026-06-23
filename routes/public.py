from flask import Blueprint, render_template, jsonify, redirect, url_for
from database import get_db_connection
from utils.logger import log_visitor

# Inisialisasi Blueprint untuk Publik
public_bp = Blueprint('public', __name__)

# ============ API ENDPOINTS (untuk React) ============
@public_bp.route('/api/public/home', methods=['GET'])
def api_home():
    """Return data untuk halaman utama React"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute("SELECT config_value FROM site_config WHERE config_key = 'hero_image'")
    hero_data = cursor.fetchone()
    hero_image_path = hero_data['config_value'] if hero_data else '/static/uploads/default_hero.jpg'

    cursor.execute("SELECT * FROM berita ORDER BY created_at DESC LIMIT 3")
    berita_list = cursor.fetchall()
    for berita in berita_list:
        if berita['created_at']:
            berita['created_at'] = berita['created_at'].strftime("%d %b %Y")
            
    cursor.execute("SELECT * FROM program_kerja")
    proker_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'hero_image': hero_image_path,
        'berita_list': berita_list,
        'proker_list': proker_list
    })

@public_bp.route('/api/public/struktur', methods=['GET'])
def api_struktur():
    """Return data struktur organisasi"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute("SELECT * FROM struktur ORDER BY id ASC")
    struktur_list = cursor.fetchall()
    
    struktur_grouped = {}
    for person in struktur_list:
        div = person['divisi']
        if div not in struktur_grouped:
            struktur_grouped[div] = []
        struktur_grouped[div].append(person)
    
    cursor.close()
    conn.close()
    
    return jsonify({'struktur_grouped': struktur_grouped})

@public_bp.route('/api/public/berita/<int:id>', methods=['GET'])
def api_berita_detail(id):
    """Return data berita detail"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute("SELECT * FROM berita WHERE id = %s", (id,))
    berita = cursor.fetchone()
    
    if not berita:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Berita tidak ditemukan'}), 404
        
    if berita['created_at']:
        berita['created_at'] = berita['created_at'].strftime("%d %b %Y")
        
    cursor.execute("SELECT * FROM berita WHERE id != %s ORDER BY created_at DESC LIMIT 3", (id,))
    berita_lainnya = cursor.fetchall()
    for b in berita_lainnya:
        if b['created_at']:
            b['created_at'] = b['created_at'].strftime("%d %b %Y")
            
    cursor.close()
    conn.close()
    
    return jsonify({
        'berita': berita,
        'berita_lainnya': berita_lainnya
    })

# ============ TEMPLATE ENDPOINTS (Jika masih diperlukan untuk backward compatibility) ============
@public_bp.route('/', methods=['GET'])
def index():
    log_visitor("Beranda (Home)")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute("SELECT config_value FROM site_config WHERE config_key = 'hero_image'")
    hero_data = cursor.fetchone()
    hero_image_path = hero_data['config_value'] if hero_data else '/static/uploads/default_hero.jpg'

    cursor.execute("SELECT * FROM berita ORDER BY created_at DESC LIMIT 3")
    berita_list = cursor.fetchall()
    for berita in berita_list:
        if berita['created_at']:
            berita['created_at'] = berita['created_at'].strftime("%d %b %Y")
            
    cursor.execute("SELECT * FROM program_kerja")
    proker_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('public/index.html', 
                           hero_image=hero_image_path,
                           berita_list=berita_list, 
                           proker_list=proker_list)

@public_bp.route('/struktur', methods=['GET'])
def struktur():
    log_visitor("Halaman Struktur")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute("SELECT * FROM struktur ORDER BY id ASC")
    struktur_list = cursor.fetchall()
    
    struktur_grouped = {}
    for person in struktur_list:
        div = person['divisi']
        if div not in struktur_grouped:
            struktur_grouped[div] = []
        struktur_grouped[div].append(person)
    
    cursor.close()
    conn.close()
    
    return render_template('public/struktur.html', struktur_grouped=struktur_grouped)

@public_bp.route('/berita/<int:id>', methods=['GET'])
def berita_detail(id):
    log_visitor(f"Membaca Berita ID: {id}")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) 
    
    cursor.execute("SELECT * FROM berita WHERE id = %s", (id,))
    berita = cursor.fetchone()
    
    if not berita:
        cursor.close()
        conn.close()
        return redirect(url_for('public.index'))
        
    if berita['created_at']:
        berita['created_at'] = berita['created_at'].strftime("%d %b %Y")
        
    cursor.execute("SELECT * FROM berita WHERE id != %s ORDER BY created_at DESC LIMIT 3", (id,))
    berita_lainnya = cursor.fetchall()
    for b in berita_lainnya:
        if b['created_at']:
            b['created_at'] = b['created_at'].strftime("%d %b %Y")
            
    cursor.close()
    conn.close()
    
    return render_template('public/berita_detail.html', berita=berita, berita_lainnya=berita_lainnya)

@public_bp.route('/berita')
def semua_berita():
    log_visitor("Halaman Semua Berita")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Ambil semua berita, urutkan dari yang terbaru (sesuai default dropdown 'Paling Baru')
    cursor.execute("SELECT * FROM berita ORDER BY created_at DESC")
    berita_list = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('public/berita.html', berita_list=berita_list)

