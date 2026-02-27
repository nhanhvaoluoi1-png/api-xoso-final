from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)
CORS(app)

def crawl_mien(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://xoso.com.vn/"
    }
    for _ in range(3): # Thử lại 3 lần nếu bị lỗi
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                res.encoding = 'utf-8'
                return BeautifulSoup(res.text, "html.parser")
        except:
            time.sleep(1)
    return None

def get_data():
    urls = {
        "Bac": "https://xoso.com.vn/",
        "Nam": "https://xoso.com.vn/xo-so-mien-nam/xsmn-p1.html",
        "Trung": "https://xoso.com.vn/xo-so-mien-trung/xsmt-p1.html"
    }
    final_results = {"Bac": {}, "Nam": {}, "Trung": {}}

    for mien, url in urls.items():
        soup = crawl_mien(url)
        if not soup: continue
        
        tables = soup.find_all("table", class_="table-result")
        for table in tables:
            # Lấy tên các đài từ header
            header = table.find("tr", class_="tr-header")
            if not header: continue
            
            tinh_links = header.find_all("a")
            tinh_names = [a.text.strip().upper() for a in tinh_links if a.text.strip()]
            
            # Khởi tạo data cho từng đài
            tinh_data = {tinh: {} for tinh in tinh_names}
            
            rows = table.find_all("tr")
            for row in rows:
                giai_cell = row.find("td", class_="txt-giai")
                if not giai_cell: continue
                
                name_giai = giai_cell.text.strip().upper()
                if "ĐẶC BIỆT" in name_giai: name_giai = "DB"
                
                # Lấy số của từng đài
                v_giais = row.find_all("td", class_="v-giai")
                for i, v_giai in enumerate(v_giais):
                    if i < len(tinh_names):
                        tinh = tinh_names[i]
                        # Tìm tất cả số trong ô (đề phòng G6, G4 có nhiều số)
                        nums = [span.text.strip() for span in v_giai.find_all("span") if span.text.strip()]
                        if nums:
                            tinh_data[tinh][name_giai] = nums
            
            final_results[mien].update(tinh_data)
            
    return final_results

@app.route('/api/xoso')
def api_xoso():
    data = get_data()
    # Kiểm tra nếu rỗng hết thì báo lỗi để app biết
    status = "success" if any(data.values()) else "error"
    return jsonify({"status": status, "data": data})

@app.route('/')
def home():
    return "Xo So API VIP is running!"

if __name__ == "__main__":
    app.run()

