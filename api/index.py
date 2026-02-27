from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

def get_data_tu_web():
    urls = {
        "Bac": "https://xoso.com.vn/",
        "Nam": "https://xoso.com.vn/xo-so-mien-nam/xsmn-p1.html",
        "Trung": "https://xoso.com.vn/xo-so-mien-trung/xsmt-p1.html"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    final_results = {}

    for mien, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Lấy tất cả các bảng kết quả
            tables = soup.find_all("table", class_="table-result")
            mien_data = {}

            for table in tables:
                # Tìm tất cả span có chứa ID giải thưởng
                spans = table.find_all("span", id=re.compile(r"prize"))
                for s in spans:
                    sid = s.get('id')
                    # Cấu trúc ID thường là: VL_prizeDb hoặc BD_prize1
                    match = re.search(r"([A-Z]+)_prize(.+)", sid, re.IGNORECASE)
                    if match:
                        ma_dai = match.group(1).upper()
                        ten_giai = match.group(2).upper()
                        # Chuẩn hóa tên giải Đặc biệt
                        if "DB" in ten_giai: ten_giai = "DB"
                        
                        so = s.text.strip()
                        if so and so.isdigit():
                            if ma_dai not in mien_data: mien_data[ma_dai] = {}
                            if ten_giai not in mien_data[ma_dai]: mien_data[ma_dai][ten_giai] = []
                            if so not in mien_data[ma_dai][ten_giai]:
                                mien_data[ma_dai][ten_giai].append(so)
            
            final_results[mien] = mien_data
        except Exception as e:
            final_results[mien] = {"error": str(e)}
            
    return final_results

@app.route('/api/xoso')
def api_xoso():
    data = get_data_tu_web()
    return jsonify({"ngay": "Latest", "data": data})

@app.route('/')
def home():
    return "API Xoso is running! Go to /api/xoso"

if __name__ == "__main__":
    app.run()
