from flask import Flask, render_template
import os
import json

app = Flask(__name__, template_folder="templates")

with open("copy.json") as f:
    copy = json.load(f)

@app.route("/")
def index():
    return render_template("index.html", copy=copy)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
