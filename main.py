from io import StringIO

from flask import Flask, render_template, g, request
from markdown import markdown, Markdown
from werkzeug.exceptions import NotFound

import db

app = Flask(__name__)


@app.template_filter()
def md(string: str) -> str:
    return markdown(string)


# https://stackoverflow.com/a/54923798/12519972
def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


Markdown.output_formats["plain"] = unmark_element


@app.template_filter()
def md2plain(string: str) -> str:
    _md = Markdown(output_format="plain")  # noqa
    _md.stripTopLevelTags = False
    return _md.convert(string)


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
    data = g.db.get_articles()
    return render_template("articles.html", articles=data)


@app.route("/articles/<int:article_id>")
def article(article_id: int):
    data = g.db.get_article(article_id)
    if data is None:
        raise NotFound("Статья не найдена")
    return render_template("article.html", article=data)


@app.route("/forum/")
def forum():
    return render_template("todo.html"), 418


@app.route("/about")
def about():
    return render_template("about.html")
