from sqlite3 import connect, Row
from typing import Any, Optional


class Database:
    def __init__(self, filename: str = "app.db"):
        self._db = connect(filename)
        self._db.row_factory = Row
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS visits(
                ip TEXT NOT NULL PRIMARY KEY,
                time INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
            );
            CREATE TABLE IF NOT EXISTS articles(
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                text TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tags(
                name TEXT PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS article_tags(
                tag TEXT REFERENCES tags(name) ON UPDATE CASCADE ON DELETE CASCADE,
                article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
                PRIMARY KEY (tag, article_id)
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

    def site_visited(self, ip: str) -> None:
        self._db.execute(
            "INSERT INTO visits(ip) VALUES (?)"
            " ON CONFLICT (ip) DO UPDATE SET time=strftime('%s', 'now')"
            ,
            (ip,)
        )

    def get_visitors(self) -> int:
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

    def get_articles(self) -> list[dict[str, Any]]:
        res = []
        for row in self._db.execute("SELECT * FROM articles"):
            tags = [
                r["tag"]
                for r in self._db.execute("SELECT tag FROM article_tags WHERE article_id=?", (row["id"],))
            ]
            res.append(
                {
                    key: row[key]
                    for key in row.keys()
                }
            )
            res[-1]["tags"] = tags
        return res

    def get_article(self, article_id: int) -> Optional[dict[str, Any]]:
        article = self._db.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()
        if article is None:
            return None
        tags = [
            r["tag"]
            for r in self._db.execute("SELECT tag FROM article_tags WHERE article_id=?", (article_id,))
        ]
        res = {
            key: article[key]
            for key in article.keys()
        }
        res["tags"] = tags
        return res
