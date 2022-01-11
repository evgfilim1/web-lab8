from sqlite3 import connect


class Database:
    def __init__(self, filename: str = "app.db"):
        self._db = connect(filename)
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS visits(
                ip TEXT NOT NULL PRIMARY KEY,
                time INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
            );
            CREATE TABLE IF NOT EXISTS users(
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS threads(
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT REFERENCES users(username) ON UPDATE CASCADE ON DELETE SET NULL,
                is_locked INTEGER CHECK ( is_locked IN (0, 1) )
            );
            CREATE TABLE IF NOT EXISTS posts(
                id INTEGER PRIMARY KEY,
                thread_id INTEGER REFERENCES threads(id),
                content TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    def __del__(self):
        self._db.commit()
        self._db.close()

    def site_visited(self, ip: str):
        self._db.execute(
            "INSERT INTO visits(ip) VALUES (?)"
            " ON CONFLICT (ip) DO UPDATE SET time=strftime('%s', 'now')"
            ,
            (ip,)
        )

    def get_visitors(self):
        cur = self._db.execute(
            "SELECT count(*)"
            " FROM visits"
            " WHERE time<=cast(strftime('%s', 'now') AS INTEGER)"
            "   AND time>=cast(strftime('%s', 'now') AS INTEGER) - 300"
            " GROUP BY ip"
            ,
        )
        if res := cur.fetchone():
            return res[0]
        return 0
