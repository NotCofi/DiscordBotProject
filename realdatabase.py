import sqlite3
import os


class puckvault():
    def __init__(self, db_path="puck_vault.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.setup()

    def setup(self):
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
                               (
                                   user_id          INTEGER PRIMARY KEY NOT NULL,
                                   balance          INTEGER NOT NULL DEFAULT 0,
                                   last_daily_claim TIMESTAMP
                               );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS matches
                               (
                                   match_id   INTEGER PRIMARY KEY,
                                   home_team  TEXT,
                                   away_team  TEXT,
                                   start_time TIMESTAMP,
                                   status     TEXT,
                                   result     TEXT
                               );""")

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bets
                               (
                                   bet_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                                   user_id  INTEGER,
                                   match_id INTEGER,
                                   amount   INTEGER,
                                   team     TEXT,
                                   odds     INTEGER,
                                   FOREIGN KEY (user_id) REFERENCES users (user_id),
                                   FOREIGN KEY (match_id) REFERENCES matches (match_id)
                               );""")
        self.conn.commit()

    def create_user(self, users):
        self.cursor.execute(
            "INSERT INTO users DEFAULT VALUES"
        )
        self.conn.commit()

    def get_user(self, user_id):
        self.cursor.execute(
            "SELECT * FROM users WHERE user_id = ?"
        )
        return self.cursor.fetchone()

    def update_balance(self, amount, user_id):
        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id)
        )
        self.conn.commit()

    def create_match(self, match_id, home_team, away_team, start_time, result, status):
        self.cursor.execute(
            "INSERT INTO matches (match_id, home_team, away_team, start_time, status, result) VALUES (?, ?, ?, ?, ?, ?)"
        )
        self.conn.commit()

    def update_match_result(self, match_id, result):
        self.cursor.execute("UPDATE matches SET result = ?, status = 'finished' WHERE match_id = ?", (result, match_id))
        self.conn.commit()

    def get_upcoming_matches(self):
        self.cursor.execute("SELECT * FROM matches WHERE status  = 'upcoming'")
        return self.cursor.fetchall()

    def place_bet(self, user_id, match_id, team, amount, odds):
        self.cursor.execute("INSERT INTO bets (user_id, match_id, amount, team, odds) VALUES (?, ?, ?, ?, ?)")
        self.conn.commit()

    def get_bets_for_match(self, match_id):
        self.cursor.execute("SELECT * FROM bets WHERE match_id = ?")
        return self.cursor.fetchall()

    def resolve_bets(self, match_id):
        self.cursor.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
        match_info = self.cursor.fetchone()
        winning_team = match_info["result"]
        self.cursor.execute("SELECT * FROM bets WHERE match_id = ? AND team = ?", (match_id, winning_team))
        return self.cursor.fetchall()



    def close(self):
        self.conn.close()
