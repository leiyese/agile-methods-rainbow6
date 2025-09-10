from flask import Flask
import os

app = Flask(__name__)


@app.route("/")
def index():
    return "Hello Rainbow 6!"

@app.route("/daniel")
def daniel():
    return "Hello Rainbow 6! This is Daniel"

@app.route("/hua")
def hua():
    return fel ms

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
