from flask import Flask, request, render_template_string, redirect
import json
import datetime
from pathlib import Path

app = Flask(__name__)

CODEX_FILE = Path("gemma_michael_codex.json")

def load_codex():
    if CODEX_FILE.exists():
        with open(CODEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {"entries": []}

def save_codex(codex):
    with open(CODEX_FILE, "w", encoding="utf-8") as f:
        json.dump(codex, f, indent=2)

@app.route("/", methods=["GET", "POST"])
def index():
    codex = load_codex()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form.get("tags", "").split(",")
        entry = {
            "title": title,
            "content": content,
            "tags": [t.strip() for t in tags if t.strip()],
            "date": str(datetime.datetime.now())
        }
        codex["entries"].append(entry)
        save_codex(codex)
        return redirect("/")

    query = request.args.get("q", "")
    entries = codex["entries"]
    if query:
        entries = [
            e for e in entries
            if query.lower() in e["title"].lower() or query.lower() in e["content"].lower()
        ]

    template = """
    <html>
      <head>
        <title>Gemma–Michael Codex</title>
        <style>
          body { background: black; color: lime; font-family: monospace; padding: 20px; }
          h1 { text-shadow: 0 0 10px lime; }
          input, textarea { width: 100%; margin: 5px 0; padding: 8px; background: #111; color: lime; border: 1px solid lime; }
          button { background: lime; color: black; padding: 8px 15px; font-weight: bold; border: none; cursor: pointer; }
          .entry { border: 1px solid lime; padding: 10px; margin-bottom: 10px; }
        </style>
      </head>
      <body>
        <h1>⚔️ Gemma–Michael Codex ⚔️</h1>
        <form method="GET">
          <input type="text" name="q" placeholder="Search..." value="{{query}}">
          <button type="submit">Search</button>
        </form>
        <h2>Add New Entry</h2>
        <form method="POST">
          <input type="text" name="title" placeholder="Title">
          <textarea name="content" placeholder="Content"></textarea>
          <input type="text" name="tags" placeholder="Tags (comma separated)">
          <button type="submit">Add Entry</button>
        </form>
        <h2>Entries</h2>
        {% for e in entries %}
          <div class="entry">
            <h3>{{e.title}}</h3>
            <p>{{e.content}}</p>
            <small>Tags: {{e.tags}} | Date: {{e.date}}</small>
          </div>
        {% endfor %}
      </body>
    </html>
    """
    return render_template_string(template, entries=entries, query=query)

if __name__ == "__main__":
    app.run(debug=True)
