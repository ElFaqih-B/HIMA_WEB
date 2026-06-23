# utils/activity_logger.py
from flask import request, session
from database import get_db_connection

def log_activity(aktivitas):
    """Mencatat aktivitas admin ke dalam activity_logs"""
    admin_id = session.get('admin_id') # Mengambil ID dari session login
    
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
    """Mencatat IP pengunjung publik ke dalam visitor_logs"""
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