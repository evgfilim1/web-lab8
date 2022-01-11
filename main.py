from markdown import markdown
from flask import Flask, render_template, g, request

import db

app = Flask(__name__)

fake_articles = [
    {
        "id": 1,
        "title": "Test",
        "text": "Lorem ipsum blah blah",
        "tags": ["test"],
    },
    {
        "id": 2,
        "title": "Longer test",
        "text": ("**Lorem** _ipsum_ dolor `sit` ~~amet~~ " * 1024),
        "tags": ["test", "long"],
    },
]


@app.template_filter()
def md(string: str):
    return markdown(string)


@app.before_request
def connect_db():
    g.db = db.Database()
    g.db.site_visited(request.remote_addr)


@app.teardown_request
def commit_db(_):
    del g.db


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/articles/")
def articles():
    return render_template("articles.html", articles=fake_articles)


@app.route("/articles/<int:article_id>")
def article(article_id: int):
    return render_template("article.html", article=fake_articles[article_id - 1])


@app.route("/forum/")
def forum():
    return render_template("todo.html"), 418


@app.route("/about")
def about():
    return render_template("about.html")
