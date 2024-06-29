import sqlite3 as sq


class DatabaseManager(object):

    def __init__(self, path):
        self.conn = sq.connect(path)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def create_tables(self):
        self.query("""CREATE TABLE IF NOT EXISTS news(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT,
                   body TEXT,
                   link TEXT,
                   date TEXT)
                    """)
        self.query("""CREATE TABLE IF NOT EXISTS news_err(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT,
                   link TEXT,
                   exception TEXT)
                    """)
        return True

    def connection(self):
        return self.conn

    def query(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        self.conn.commit()

    def fetchone(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchone()

    def fetchall(self, arg, values=None):
        if values is None:
            self.cur.execute(arg)
        else:
            self.cur.execute(arg, values)
        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()
