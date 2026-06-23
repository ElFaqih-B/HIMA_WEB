# utils/logger.py
from database import get_db_connection
from flask import request, session

def log_activity(aktivitas):
    """Mencatat aktivitas admin ke dalam activity_logs"""
    admin_id = session.get('admin_id') # Pastikan saat login, admin_id disimpan ke session
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO activity_logs (admin_id, aktivitas) VALUES (%s, %s)",
        (admin_id, aktivitas)
    )
    conn.commit()
    cursor.close()
    conn.close()

def log_visitor(halaman):
    """Mencatat pengunjung publik ke dalam visitor_logs"""
    ip_address = request.remote_addr
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO visitor_logs (ip_address, halaman) VALUES (%s, %s)",
        (ip_address, halaman)
    )
    conn.commit()
    cursor.close()
    conn.close()