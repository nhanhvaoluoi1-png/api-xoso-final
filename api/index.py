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
    # Giả lập trình duyệt thật để Vercel không bị chặn
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    final_results = {}

    for mien, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Tìm tất cả các bảng kết quả (vì Nam/Trung có nhiều bảng cho nhiều đài)
            tables = soup.find_all("table", class_="table-result")
            mien_data = {}

            for table in tables:
                # Tìm tất cả các ô có chứa số giải
                spans = table.find_all("span", id=True)
                for s in spans:
                    span_id = s.get('id')
                    # Lọc các id có cấu trúc giải thưởng (ví dụ: BD_prizeDb hoặc MB_prize1)
                    if "prize" in span_id:
                        parts = span_id.split('_')
                        if len(parts) >= 2:
                            ma_dai = parts[0].upper()
                            # Chuẩn hóa tên giải: prizeDb -> DB, prize1 -> G1...
                            raw_giai = parts[1].replace('prize', '')
                            ten_giai = "DB" if raw_giai.lower() == "db" else f"G{raw_giai}"
                            
                            so = s.text.strip()
                            if so:
                                if ma_dai not in mien_data: 
                                    mien_data[ma_dai] = {}
                                if ten_giai not in mien_data[ma_dai]: 
                                    mien_data[ma_dai][ten_giai] = []
                                # Thêm số vào danh sách giải (tránh trùng)
                                if so not in mien_data[ma_dai][ten_giai]:
                                    mien_data[ma_dai][ten_giai].append(so)
            
            final_results[mien] = mien_data
        except Exception as e:
            final_results[mien] = {"error": str(e)}
            
    return final_results

@app.route('/')
def home():
    return "Xo So API is running! Truy cập /api/xoso để lấy dữ liệu."

@app.route('/api/xoso')
def api_xoso():
    data = get_data_tu_web()
    return jsonify({"ngay": "Latest", "data": data})

# Vercel cần dòng này để nhận diện app
if __name__ == "__main__":
    app.run()
