from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

def clean_giai_name(raw_name):
    """Chuẩn hóa tên giải: prizeDb -> DB, prize1 -> G1..."""
    name = raw_name.upper().replace('PRIZE', '')
    if 'DB' in name: return 'DB'
    if 'G' in name: return name
    # Nếu chỉ có số (ví dụ: 1, 2) thì thêm chữ G vào đầu
    return f"G{name}" if name.isdigit() else name

def get_data_tu_web():
    urls = {
        "Bac": "https://xoso.com.vn/",
        "Nam": "https://xoso.com.vn/xo-so-mien-nam/xsmn-p1.html",
        "Trung": "https://xoso.com.vn/xo-so-mien-trung/xsmt-p1.html"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    final_results = {"Bac": {}, "Nam": {}, "Trung": {}}

    for mien, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")
            
            tables = soup.find_all("table", class_="table-result")
            for table in tables:
                spans = table.find_all("span", id=re.compile(r"prize"))
                for s in spans:
                    sid = s.get('id')
                    match = re.search(r"([A-Z]+)_prize(.+)", sid, re.IGNORECASE)
                    if match:
                        ma_dai = match.group(1).upper()
                        # Loại bỏ đài miền Bắc (MB) khỏi danh sách miền Nam/Trung nếu bị lẫn
                        if mien != "Bac" and ma_dai == "MB": continue
                        if mien == "Bac" and ma_dai != "MB": continue
                        
                        ten_giai = clean_giai_name(match.group(2))
                        so = s.text.strip()
                        
                        if so and so.isdigit():
                            if ma_dai not in final_results[mien]: 
                                final_results[mien][ma_dai] = {}
                            if ten_giai not in final_results[mien][ma_dai]: 
                                final_results[mien][ma_dai][ten_giai] = []
                            if so not in final_results[mien][ma_dai][ten_giai]:
                                final_results[mien][ma_dai][ten_giai].append(so)
        except:
            continue
            
    return final_results

@app.route('/api/xoso')
def api_xoso():
    data = get_data_tu_web()
    return jsonify({
        "status": "success",
        "ngay": "Latest", 
        "data": data
    })

@app.route('/')
def home():
    return "VIP Xoso API is live! Use /api/xoso"

if __name__ == "__main__":
    app.run()
    app.run()

