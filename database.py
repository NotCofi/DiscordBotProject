import sqlite3

class Database:
    def __init__(self, db_path="bans"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        sql = """CREATE TABLE IF NOT EXISTS bans
                 (
                     ban_id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id TEXT NOT NULL,                                                                 
                     moderator_id TEXT NOT NULL,
                     reason TEXT,
                     timestamp DEFAULT CURRENT_TIMESTAMP
                 );"""
        self.cursor.execute(sql)
        self.conn.commit()

    def add_bans(self, user_id, moderator_id, reason):
        self.cursor.execute(
            "INSERT INTO bans (user_id, moderator_id, reason) VALUES (?, ?, ?)",
            (user_id, moderator_id, reason)
        )
        self.conn.commit()

    def get_ban(self, ban_id):
        self.cursor.execute("SELECT * FROM bans WHERE ban_id = ?", (ban_id,))
        return self.cursor.fetchone()

    def get_bans_by_user(self, user_id):
        self.cursor.execute("SELECT * FROM bans WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()

    def get_all_bans(self):
        self.cursor.execute("SELECT * FROM bans")
        return self.cursor.fetchall()


    def remove_bans_by_user(self, user_id):
        self.cursor.execute("DELETE FROM bans WHERE user_id = ?", (user_id,))
        self.conn.commit()



    def close(self):
        self.conn.close()



