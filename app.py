import pytz
from datetime import datetime
from secrets import token_urlsafe
from flask import Flask, render_template, request, redirect, abort
from flask_bootstrap import Bootstrap
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

app = Flask(__name__)
Bootstrap(app)
client = FaunaClient(secret="your-secret-here")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title").strip()
        paste_text = request.form.get("paste-text").strip()

        identifier = token_urlsafe(5)
        paste = client.query(q.create(q.collection("pastes"), {
            "data": {
                "identifier": identifier,
                "paste_text": paste_text,
                "title": title,
                "date": datetime.now(pytz.UTC)
            }
        }))

        return redirect(request.host_url + identifier)
    return render_template("index.html")


@app.route("/<string:paste_id>/")
def render_paste(paste_id):
    try:
        paste = client.query(
            q.get(q.match(q.index("paste_by_identifier"), paste_id)))
    except:
        abort(404)

    return render_template("paste.html", paste=paste["data"])


if __name__ == "__main__":
    app.run(debug=True)
