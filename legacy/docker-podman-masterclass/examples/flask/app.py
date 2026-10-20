from flask import Flask
import os

app = Flask(__name__)

@app.get("/")
def hello():
    return {"msg": "hello from flask", "engine": os.environ.get("ENGINE", "unknown")}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
