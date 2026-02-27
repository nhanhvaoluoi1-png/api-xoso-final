from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def get_data_tu_web():
    urls = {
        "Bac": "https://xoso.com.vn/",
        "Nam": "https://xoso.com.vn/xo-so-mien-nam/xsmn-p1.html",
        "Trung": "https://xoso.com.vn/xo-so-mien-trung/xsmt-p1.html"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    final_results = {}

    for mien, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")
            main_table = soup.find("table", class_="table-result")
            
            mien_data = {}
            if main_table:
                spans = main_table.find_all("span", id=lambda x: x and "prize" in x)
                for s in spans:
                    parts = s.get('id').split('_')
                    if len(parts) >= 2:
                        ma_dai = parts[0].upper()
                        ten_giai = "DB" if "Db" in parts[1] else f"G{parts[1].replace('prize','')}"
                        so = s.text.strip()
                        if so and so.isdigit():
                            if ma_dai not in mien_data: mien_data[ma_dai] = {}
                            if ten_giai not in mien_data[ma_dai]: mien_data[ma_dai][ten_giai] = []
                            if so not in mien_data[ma_dai][ten_giai]:
                                mien_data[ma_dai][ten_giai].append(so)
            final_results[mien] = mien_data
        except:
            final_results[mien] = {}
    return final_results

@app.route('/')
def home():
    return "Xo So API is running!"

@app.route('/api/xoso')
def api_xoso():
    data = get_data_tu_web()
    return jsonify({"ngay": "Latest", "data": data})

# Vercel sử dụng biến 'app' này