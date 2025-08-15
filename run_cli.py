import argparse
import os
import warnings
from datetime import datetime
from app import create_app, db
from app.models import Video
from core_analysis.AnalysisPipeline import AnalysisPipeline

warnings.filterwarnings("ignore")

def run_analysis_from_cli(video_filename, start_time, show_preview):
    app = create_app()
    with app.app_context():
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        if not os.path.exists(video_path):
            print(f"Lỗi: Không tìm thấy file video '{video_filename}'.")
            return

        print(f"Bắt đầu phân tích video: {video_filename}")

        pipeline = AnalysisPipeline(config=app.config)
        
        all_results = []
        try:
            for frame_num, timestamp, vehicles in pipeline.run_and_yield(video_path=video_path, start_time=start_time, show_preview=show_preview):
                
                # format and print out terminal
                if len(vehicles) > 0:
                    print(f"--- Frame {frame_num} ({timestamp.strftime('%H:%M:%S')}) ---")
                    for v_id, data in vehicles.items():
                        print(f"  > ID: {v_id}, Loai: {data['class_name']}, Toc do: {data['speed_kmh']:.2f} km/h")
                
                # collection for saved
                for v_id, data in vehicles.items():
                    all_results.append({
                        "timestamp": timestamp, "vehicle_id": v_id,
                        "class_name": data['class_name'], "speed_kmh": data['speed_kmh']
                    })
            
            print(f"\nHoàn tất phân tích. Tổng cộng {len(all_results)} bản ghi đã được thu thập.")

        except KeyboardInterrupt:
            print("\nNgười dùng đã dừng chương trình.")
        
        finally:
            print("Đã kết thúc pipeline.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chạy pipeline phân tích giao thông trên một file video.')
    parser.add_argument('--video', type=str, required=True, help='Tên file video (phải nằm trong instance/uploads).')
    parser.add_argument('--start-time', type=str, required=True, help="Thời gian bắt đầu. Định dạng: 'YYYY-MM-DDTHH:MM'.")
    parser.add_argument('--show-preview', action='store_true', help='Hiển thị cửa sổ xem trước.')

    args = parser.parse_args()
    try:
        start_time_dt = datetime.fromisoformat(args.start_time)
    except ValueError:
        print("Lỗi: Định dạng --start-time không hợp lệ."); exit()

    run_analysis_from_cli(args.video, start_time_dt, args.show_preview)
    