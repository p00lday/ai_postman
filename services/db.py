import sqlite3

DB_PATH = "database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Добавили is_active (1 = подписан, 0 = отписан)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            topics TEXT,
            is_active INTEGER DEFAULT 1 
        )
    ''')
    conn.commit()
    conn.close()

def add_user_if_not_exists(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Мягкое добавление: если юзер есть, игнорируем
    cursor.execute('INSERT OR IGNORE INTO users (user_id, is_active) VALUES (?, 1)', (user_id,))
    conn.commit()
    conn.close()

def set_user_topics(user_id, topics_list):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    topics_str = ",".join(topics_list)
    cursor.execute('UPDATE users SET topics = ? WHERE user_id = ?', (topics_str, user_id))
    conn.commit()
    conn.close()

def get_user_topics(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT topics FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0].split(",") if result and result[0] else None

def set_active_status(user_id, is_active):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_active = ? WHERE user_id = ?', (is_active, user_id))
    conn.commit()
    conn.close()

def get_all_subscribers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Берем только подписанных юзеров, у которых заданы темы
    cursor.execute('SELECT user_id, topics FROM users WHERE is_active = 1 AND topics IS NOT NULL')
    users = cursor.fetchall()
    conn.close()
    return users