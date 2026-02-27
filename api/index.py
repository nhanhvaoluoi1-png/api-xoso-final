from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

def get_xoso_all():
    urls = {
        "Bac": "https://xoso.com.vn/",
        "Nam": "https://xoso.com.vn/xo-so-mien-nam/xsmn-p1.html",
        "Trung": "https://xoso.com.vn/xo-so-mien-trung/xsmt-p1.html"
    }
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    results = {"Bac": {}, "Nam": {}, "Trung": {}}

    for mien, url in urls.items():
        try:
            res = requests.get(url, headers=headers, timeout=15)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")
            
            # Tìm tất cả các bảng kết quả
            tables = soup.find_all("table", class_="table-result")
            for table in tables:
                # 1. Lấy danh sách tên các đài (nằm ở hàng đầu tiên của bảng)
                header_row = table.find("tr", class_="tr-header")
                if not header_row: continue
                
                # Tìm các chữ viết tắt đài (ví dụ: Vĩnh Long -> VL)
                tinh_names = [a.text.strip().upper() for a in header_row.find_all("a") if a.text.strip()]
                if not tinh_names: continue
                
                # Khởi tạo dữ liệu cho từng đài trong mien_data
                temp_mien_data = {tinh: {} for tinh in tinh_names}

                # 2. Duyệt qua từng hàng giải (G8, G7... DB)
                rows = table.find_all("tr")
                for row in rows:
                    label_cell = row.find("td", class_="txt-giai")
                    if not label_cell: continue
                    
                    giai_name = label_cell.text.strip().upper() # VD: "GIẢI ĐẶC BIỆT" hoặc "G8"
                    # Chuẩn hóa tên giải cho app dễ quét
                    if "ĐẶC BIỆT" in giai_name: giai_name = "DB"
                    
                    # Lấy tất cả các ô chứa số ở hàng này
                    number_cells = row.find_all("td", class_="v-giai")
                    
                    # Mỗi ô number_cells tương ứng với 1 đài theo thứ tự tinh_names
                    for idx, cell in enumerate(number_cells):
                        if idx < len(tinh_names):
                            tinh = tinh_names[idx]
                            # Lấy tất cả các số trong ô (nếu giải có nhiều số như G6, G4)
                            numbers = [span.text.strip() for span in cell.find_all("span") if span.text.strip()]
                            if numbers:
                                temp_mien_data[tinh][giai_name] = numbers

                # Gộp dữ liệu vào kết quả cuối cùng
                results[mien].update(temp_mien_data)
        except Exception as e:
            print(f"Lỗi tại {mien}: {e}")
            
    return results

@app.route('/api/xoso')
def api_xoso():
    data = get_xoso_all()
    return jsonify({"status": "success", "data": data})

@app.route('/')
def home():
    return "API Xoso Final is running!"

if __name__ == "__main__":
    app.run()
