import os
from dotenv import load_dotenv

# indentify url of main folder
basedir = os.path.abspath(os.path.dirname(__file__))
# install enviroment from file .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """
    config class base app
    """
    # config FLASK
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key-you-should-change'

    # config DATABASE (SQLALCHEMY)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # config UPLOAD FILE
    UPLOAD_FOLDER = os.path.join(basedir, 'instance', 'uploads')
    PROCESSED_FOLDER = os.path.join(basedir, 'instance', 'processed')
    ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
    
    # Config CELERY 
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://127.0.0.1:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://127.0.0.1:6379/0'
    CELERY_IMPORTS = ('tasks.video_tasks',)
    
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        'visibility_timeout': 3600,  # Thời gian tối đa một tác vụ có thể chạy (1 giờ)
        'socket_connect_timeout': 30, # Thời gian chờ để kết nối
        'socket_keepalive': True     # Bật tín hiệu "keep-alive" để giữ kết nối
    }
    
    # config analyst videos (CORE_ANALYSIS)
    ANALYSIS_CONFIDENCE_THRESHOLD = 0.35
    ANALYSIS_REAL_WORLD_WIDTH_METERS = 14.0
    ANALYSIS_PROCESSING_RESOLUTION_WIDTH = 640
    ANALYSIS_FRAME_SKIPPING_RATE = 2 # Xử lý 1 trên 2 frame
    YOLO_MODEL_PATH = os.path.join(basedir, 'core_analysis', 'models', 'yolov5s.pt')

    DASHBOARD_COLORS = {
        'car': '#1f77b4', 'motorcycle': '#ff7f0e',
        'bus': '#d62728', 'truck': '#9467bd'
    }
    
    # Config streamlib
    STREAMLIT_URL = os.environ.get('STREAMLIT_URL') or 'http://localhost:8501'

