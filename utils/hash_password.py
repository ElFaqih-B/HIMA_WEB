# utils/hash_password.py — jalankan SEKALI untuk hash password lama
# python utils/hash_password.py
import bcrypt
from database import get_db_connection

def hash_existing_passwords():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, password FROM admin")
    for admin in cursor.fetchall():
        pw = admin['password']
        if not pw.startswith('$2b$'):
            hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("UPDATE admin SET password=%s WHERE id=%s", (hashed, admin['id']))
            print(f"✅ Admin ID {admin['id']} di-hash.")
        else:
            print(f"⏭️  Admin ID {admin['id']} sudah di-hash, skip.")
    db.commit()
    cursor.close()
    db.close()

if __name__ == '__main__':
    hash_existing_passwords()