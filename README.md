# Ứng dụng Web Phân Tích Giao Thông v1.0

Đây là một ứng dụng web hoàn chỉnh được xây dựng bằng Python và Flask, sử dụng các công nghệ Thị giác Máy tính (YOLOv5, DeepSORT) và xử lý nền (Celery, Redis) để phân tích lưu lượng, mật độ, và tốc độ của các phương tiện giao thông từ video.

## 🚀 Tính năng chính

- **Giao diện Web Thân thiện**: Người dùng có thể dễ dàng tải lên, quản lý và xem kết quả phân tích video thông qua một giao diện web trực quan.
- **Xử lý Nền Mạnh mẽ**: Sử dụng **Celery** và **Redis**, các video được xử lý ở chế độ nền, giúp giao diện web luôn mượt mà và không bị treo, ngay cả khi đang phân tích các video dài.
- **Tối ưu hóa Hiệu suất trên CPU**: Tích hợp các kỹ thuật **Giảm độ phân giải xử lý** và **Bỏ qua Khung hình (Frame Skipping)** để tăng tốc độ phân tích một cách đáng kể mà không cần GPU.
- **Theo dõi Ổn định (Robust Tracking)**: Tích hợp thuật toán **DeepSORT** để duy trì ID của các phương tiện một cách ổn định, xử lý tốt các tình huống che khuất hoặc giao thông đông đúc.
- **Phân tích Ùn tắc**: Sử dụng logic **"Vùng Giám sát" (Monitoring Zone)**, hệ thống có thể theo dõi và tính toán tốc độ tức thời của tất cả các phương tiện, kể cả khi chúng đang đứng yên.
- **Dashboard Tương tác**: Mỗi video sau khi phân tích sẽ có một trang dashboard riêng (xây dựng bằng Streamlit) với các biểu đồ chi tiết về mật độ, tốc độ, phân bổ và so sánh giữa các loại xe.
- **Công cụ Dòng lệnh (CLI)**: Cung cấp script `run_cli.py` cho các nhà phát triển để chạy phân tích hàng loạt hoặc gỡ lỗi, với tùy chọn hiển thị cửa sổ xem trước.

## 🧰 Công nghệ sử dụng

- **Web Framework**: Flask, Flask-SQLAlchemy
- **Xử lý Nền**: Celery, Redis
- **Computer Vision**: OpenCV, Ultralytics (YOLOv5)
- **Tracking**: DeepSORT (`deep-sort-realtime`)
- **Data Processing**: Pandas, NumPy
- **Dashboarding**: Streamlit, Plotly

## ⚙️ Cài đặt và Chuẩn bị

Thực hiện các bước sau để cài đặt môi trường và chạy dự án.

**1. Clone Repository**

```bash
git clone <URL_CUA_BAN>
cd TrafficAnalysisWebApp
```

**2. Cài đặt Redis**
Hệ thống xử lý nền Celery yêu cầu Redis.

- **Trên Windows:** Cài đặt thông qua WSL (Windows Subsystem for Linux) hoặc tải các bản build không chính thức từ [tpor/redis-windows](https://github.com/tpor/redis-windows/releases).
- **Trên macOS:** `brew install redis`
- **Trên Ubuntu/Debian:** `sudo apt-get install redis-server`
  Sau khi cài đặt, hãy đảm bảo server Redis đang chạy.

**3. Tạo và kích hoạt Môi trường ảo**

```bash
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
```

**4. Cài đặt các thư viện Python**

```bash
pip install -r requirements.txt
```

**5. Chuẩn bị Mô hình YOLOv5 (QUAN TRỌNG)**
Dự án được thiết lập để chạy YOLOv5 hoàn toàn từ các file cục bộ.

- **Tạo thư mục**: Bên trong thư mục `core_analysis/`, hãy tạo một thư mục mới tên là `models`.
- **Tải file trọng số**: Tải file `yolov5s.pt` từ [trang release của YOLOv5](https://github.com/ultralytics/yolov5/releases) và đặt nó vào trong thư mục `core_analysis/models/`.
- **Clone mã nguồn YOLOv5**: Mở terminal tại thư mục `core_analysis/models/` và chạy lệnh sau:
  ```bash
  git clone https://github.com/ultralytics/yolov5.git
  ```
  Thao tác này sẽ tạo một thư mục `core_analysis/models/yolov5/`.

## 💡 Hướng dẫn sử dụng

Dự án có thể được chạy theo hai chế độ: Giao diện Web hoặc Dòng lệnh.

### Chế độ 1: Giao diện Web (Dành cho Người dùng cuối)

**Bước 1: Khởi động Celery Worker**
Mở một **Terminal thứ nhất** tại thư mục gốc của dự án và chạy lệnh sau. Worker này sẽ lắng nghe và thực hiện các tác vụ phân tích.

```bash
celery -A tasks.video_tasks.celery worker --loglevel=info
```

**Bước 2: Khởi động Ứng dụng Web**
Mở một **Terminal thứ hai** tại thư mục gốc và chạy lệnh sau để khởi động server Flask:

```bash
python run_web.py
```

**Bước 3: Sử dụng Ứng dụng**

- Mở trình duyệt và truy cập vào `http://127.0.0.1:5000`.
- Sử dụng giao diện để tải lên video.
- Theo dõi trạng thái xử lý trên trang chủ và trong cửa sổ terminal của Celery worker.
- Khi video đã xử lý xong, nhấp vào "Xem Dashboard" để xem kết quả.

_(Lưu ý: Phần nhúng Streamlit sẽ được triển khai ở các bước phát triển tiếp theo)_

### Chế độ 2: Dòng lệnh (Dành cho Lập trình viên)

Chế độ này cho phép bạn chạy phân tích trực tiếp và nhanh chóng.

**Bước 1: Đặt Video**

- Đặt file video của bạn (ví dụ: `my_video.mp4`) vào thư mục `instance/uploads/`. Thư mục này sẽ được tự động tạo trong lần chạy đầu tiên.

**Bước 2: Chạy Lệnh**

- Mở Terminal tại thư mục gốc của dự án.
- **Để chạy phân tích nhanh (không xem trước):**
  ```bash
  python run_cli.py --video my_video.mp4
  ```
- **Để chạy và xem quá trình xử lý:**
  ```bash
  python run_cli.py --video my_video.mp4 --show-preview
  ```

celery -A celery_worker.celery worker --loglevel=info --pool=eventlet

python run_web.py

streamlit run visualization/dashboard_streamlit.py
streamlit run visualization/dashboard_streamlit.py --server.address=0.0.0.0
