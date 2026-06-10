import sqlite3
import os
import uuid

DB_PATH = os.path.join(os.path.dirname(__file__), "stars_bot.db")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS links (
                id          TEXT PRIMARY KEY,
                admin_id    INTEGER NOT NULL,
                amount      INTEGER NOT NULL,
                label       TEXT NOT NULL,
                message     TEXT,
                invoice_url TEXT,
                active      INTEGER DEFAULT 1,
                created_at  TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS payments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                link_id     TEXT NOT NULL,
                user_id     INTEGER NOT NULL,
                username    TEXT,
                stars       INTEGER NOT NULL,
                paid_at     TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (link_id) REFERENCES links(id)
            );
        """)
        # Add invoice_url column if upgrading from old DB
        try:
            self.conn.execute("ALTER TABLE links ADD COLUMN invoice_url TEXT")
            self.conn.commit()
        except Exception:
            pass

    def create_link(self, admin_id: int, amount: int, label: str) -> str:
        link_id = str(uuid.uuid4())[:8].upper()
        self.conn.execute(
            "INSERT INTO links (id, admin_id, amount, label) VALUES (?, ?, ?, ?)",
            (link_id, admin_id, amount, label)
        )
        self.conn.commit()
        return link_id

    def save_invoice_url(self, link_id: str, url: str):
        self.conn.execute(
            "UPDATE links SET invoice_url = ? WHERE id = ?",
            (url, link_id)
        )
        self.conn.commit()

    def get_link(self, link_id: str):
        row = self.conn.execute(
            "SELECT * FROM links WHERE id = ? AND active = 1", (link_id,)
        ).fetchone()
        return dict(row) if row else None

    def set_custom_message(self, link_id: str, admin_id: int, message: str) -> bool:
        cur = self.conn.execute(
            "UPDATE links SET message = ? WHERE id = ? AND admin_id = ? AND active = 1",
            (message, link_id, admin_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def get_admin_links(self, admin_id: int):
        rows = self.conn.execute("""
            SELECT l.*, COUNT(p.id) as payment_count
            FROM links l
            LEFT JOIN payments p ON p.link_id = l.id
            WHERE l.admin_id = ? AND l.active = 1
            GROUP BY l.id
            ORDER BY l.created_at DESC
        """, (admin_id,)).fetchall()
        return [dict(r) for r in rows]

    def delete_link(self, link_id: str, admin_id: int) -> bool:
        cur = self.conn.execute(
            "UPDATE links SET active = 0 WHERE id = ? AND admin_id = ?",
            (link_id, admin_id)
        )
        self.conn.commit()
        return cur.rowcount > 0

    def record_payment(self, link_id: str, user_id: int, username: str, stars: int):
        self.conn.execute(
            "INSERT INTO payments (link_id, user_id, username, stars) VALUES (?, ?, ?, ?)",
            (link_id, user_id, username, stars)
        )
        self.conn.commit()

    def get_stats(self, admin_id: int) -> dict:
        row = self.conn.execute("""
            SELECT
                COUNT(DISTINCT l.id) as total_links,
                COUNT(p.id) as total_payments,
                COALESCE(SUM(p.stars), 0) as total_stars
            FROM links l
            LEFT JOIN payments p ON p.link_id = l.id
            WHERE l.admin_id = ? AND l.active = 1
        """, (admin_id,)).fetchone()
        return dict(row) if row else {"total_links": 0, "total_payments": 0, "total_stars": 0}


db = Database()
