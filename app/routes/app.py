import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from app.models.database import init_db
from app.models.storage import save_test_case, get_all_test_cases
from app.services.testcase_agent import run_generate_test_cases

app = Flask(__name__)
CORS(app)

# Initialize DB
init_db()

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    user_story = data.get("user_story")
    model_choice = data.get("model_choice", "openai")

    print(f"[DEBUG] Model choice received: {model_choice}")  # <-- ADD THIS

    if not user_story:
        return "User story is required", 400
    try:
        test_cases = run_generate_test_cases(user_story, model_choice)
        save_test_case(user_story, test_cases)
        return jsonify({"test_cases": test_cases})
    except Exception as e:
        return str(e), 500

@app.route("/history", methods=["GET"])
def history():
    try:
        records = get_all_test_cases()
        formatted = [{"id": r[0], "user_story": r[1], "test_cases": r[2]} for r in records]
        return jsonify(formatted)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete/<int:id>", methods=["DELETE"])
def delete_test_case(id):
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "../../test.db"))
        c = conn.cursor()
        c.execute("DELETE FROM test_cases WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": f"Test case {id} deleted."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/delete_all", methods=["DELETE"])
def delete_all_test_cases():
    try:
        conn = sqlite3.connect('test.db')
        c = conn.cursor()
        c.execute("DELETE FROM test_cases")
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "All test cases deleted."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
