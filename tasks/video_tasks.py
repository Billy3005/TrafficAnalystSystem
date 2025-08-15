import os
from datetime import datetime
import pandas as pd
import warnings
from app.models import Video
from app import db
from core_analysis.AnalysisPipeline import AnalysisPipeline
from celery_worker import celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@celery.task(bind=True)
def process_video_task(self, video_id):
    """
    Tác vụ Celery để xử lý một video ở chế độ nền.
    """
    # # This command will take effect in the worker process that is executing this task.
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    
    app = celery.flask_app
    video = Video.query.get(video_id)
    if not video:
        logger.error(f"Lỗi: Không tìm thấy Video ID {video_id} trong CSDL.")
        return

    logger.info(f"Bắt đầu xử lý video ID: {video_id} - {video.original_filename}")
    video.status = 'PROCESSING'; video.processing_started_timestamp = datetime.utcnow(); db.session.commit()

    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.saved_filename)
        pipeline = AnalysisPipeline(config=app.config)
        
        if not video.real_start_time:
            raise ValueError(f"Video ID {video_id} không có thời gian bắt đầu.")
        
        all_results = []
        print_interval = 30
        
        for frame_num, timestamp, vehicles in pipeline.run_and_yield(
            video_path=video_path, 
            start_time=video.real_start_time, 
            show_preview=False
        ):
            if frame_num % print_interval == 0 and len(vehicles) > 0:
                logger.info(f"--- [Video ID: {video_id}] Frame {frame_num} ({timestamp.strftime('%H:%M:%S')}) ---")
                for v_id, data in vehicles.items():
                    logger.info(f"  > ID: {v_id}, Loai: {data['class_name']}, Toc do: {data['speed_kmh']:.2f} km/h")
            
            for v_id, data in vehicles.items():
                all_results.append({
                    "timestamp": timestamp, "vehicle_id": v_id,
                    "class_name": data['class_name'], "speed_kmh": data['speed_kmh']
                })

        if all_results:
            df = pd.DataFrame(all_results)
            processed_filename = f"{video.id}.csv"
            processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            df.to_csv(processed_filepath, index=False)
            
            df_normal_speed = df[df['speed_kmh'] < 150]
            video.total_vehicles_detected = df_normal_speed['vehicle_id'].nunique()
            if not df_normal_speed.empty: video.average_speed = df_normal_speed['speed_kmh'].mean()
            if not df_normal_speed['class_name'].empty: video.most_common_vehicle_type = df_normal_speed['class_name'].mode()[0]
            video.status = 'COMPLETED'
            logger.info(f"Hoàn tất xử lý video ID: {video_id}.")
        else:
            video.status = 'FAILED'
            logger.warning(f"Xử lý video ID: {video_id} thất bại, không có kết quả.")
    
    except Exception as e:
        video.status = 'FAILED'
        logger.error(f"Lỗi nghiêm trọng khi xử lý video ID {video_id}: {e}", exc_info=True)
        db.session.rollback()
    
    finally:
        video.processing_finished_timestamp = datetime.utcnow()
        db.session.commit()

    return {'status': video.status}