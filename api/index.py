from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Đường dẫn đến file data.json nằm cùng thư mục với requirements.txt
# (Vercel sẽ tìm file này ở thư mục gốc của project)
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data.json')

@app.route('/api/xoso')
def get_xoso():
    try:
        if os.path.exists(DATA_PATH):
            with open(DATA_PATH, 'r', encoding='utf-8') as f:
                data_json = json.load(f)
                return jsonify(data_json)
        else:
            return jsonify({"status": "error", "message": "Khong tim thay file data.json tren GitHub"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/')
def home():
    return "API Xoso phien ban on dinh dang chay!"

if __name__ == "__main__":
    app.run()
