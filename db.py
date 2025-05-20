# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def register_user(name, email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # 이메일 중복
    finally:
        conn.close()
        
def login_user(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = c.fetchone()
    conn.close()
    return user  

# 관리자 모드 > 사용자 삭제
def get_all_users():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id, name, email FROM users ORDER BY id")
    users = c.fetchall()
    conn.close()
    return users

def delete_user_by_email(email):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    
# 랭킹 카운트
def init_user_stats():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_stats (
            email TEXT PRIMARY KEY,
            name TEXT,
            total_attempts INTEGER DEFAULT 0,
            passed_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def record_test_result(email, name, score):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    passed = 1 if score >= 2 else 0  # 컷 기준

    c.execute("SELECT * FROM user_stats WHERE email = ?", (email,))
    if c.fetchone():
        c.execute("""
            UPDATE user_stats
            SET total_attempts = total_attempts + 1,
                passed_count = passed_count + ?
            WHERE email = ?
        """, (passed, email))
    else:
        c.execute("""
            INSERT INTO user_stats (email, name, total_attempts, passed_count)
            VALUES (?, ?, 1, ?)
        """, (email, name, passed))

    conn.commit()
    conn.close()

def get_user_stats(email):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT total_attempts, passed_count FROM user_stats WHERE email = ?", (email,))
    stats = c.fetchone()
    conn.close()
    return stats if stats else (0, 0)

def get_top_rankings(limit=10):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        SELECT name, passed_count
        FROM user_stats
        WHERE email != 'sw_admin'
        ORDER BY passed_count DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return rows