from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

@app.route("/send-task", methods=["POST"])
def receive_task():
    task = request.json
    with open("received_tasks.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(task, ensure_ascii=False) + "\n")
    return jsonify({"message": "Received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6789)

