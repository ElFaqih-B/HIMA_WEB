from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from database import get_db_connection
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
    
    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'Username dan password harus diisi'}), 400
        return "Username atau Password tidak lengkap!"
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
    admin = cursor.fetchone()
    
    is_valid = False
    if admin:
        try:
            # Mencoba mengecek password menggunakan bcrypt
            is_valid = bcrypt.checkpw(password.encode('utf-8'), admin['password'].encode('utf-8'))
        except ValueError:
            # JARING PENGAMAN: Jika kena "Invalid salt" (karena masih plaintext)
            # Kita cek apakah sama persis dengan teks ketikan
            if admin['password'] == password:
                # Jika sama, kita ubah jadi hash secara otomatis dan simpan ke DB
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE admin SET password = %s WHERE id = %s", (hashed_pw, admin['id']))
                conn.commit()
                is_valid = True

    cursor.close()
    conn.close()
    
    if is_valid:
        session['sudah_login'] = True
        session['username'] = admin['username']
        session['admin_id'] = admin['id']
        session['role'] = admin['role']
        
        if request.is_json:
            return jsonify({'message': 'Login berhasil', 'username': admin['username'], 'role': admin['role']}), 200
        return redirect(url_for('admin.dashboard'))
    else:
        if request.is_json:
            return jsonify({'error': 'Username atau Password salah'}), 401
        return "Username atau Password salah!"

@auth_bp.route('/logout')
def logout():
    session.clear()
    if request.is_json:
        return jsonify({'message': 'Logout berhasil'}), 200
    return redirect(url_for('auth.login'))