from flask import Flask
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello Rainbow 6!"


@app.route("/daniel")
def daniel():
    name = "Daniel"
    return f"Hello Rainbow 6! This is {name}"


@app.route("/hua")
def hua():
    return "Hello Rainbow 6! This is Hua"


@app.route("/add/<int:a>/<int:b>")
def add():
    return f"{a} + {b} = {a + b}"
  

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
