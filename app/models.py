from datetime import datetime
from app import db

class Video(db.Model):
    """
    model represented for a video uploaded and process analyst of it
    """
    id = db.Column(db.Integer, primary_key=True)
    original_filename = db.Column(db.String(150), nullable=False)
    saved_filename = db.Column(db.String(150), nullable=False, unique=True)
    upload_timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    real_start_time = db.Column(db.DateTime, nullable=True, index=True)
    status = db.Column(db.String(20), index=True, default='PENDING')
    processing_started_timestamp = db.Column(db.DateTime, nullable=True)
    processing_finished_timestamp = db.Column(db.DateTime, nullable=True)
    total_vehicles_detected = db.Column(db.Integer, default=0)
    average_speed = db.Column(db.Float, default=0.0)
    most_common_vehicle_type = db.Column(db.String(50), nullable=True)
    celery_task_id = db.Column(db.String(150), nullable=True)

    # 1-n relationship with log
    logs = db.relationship("VehicleLog", backref="video", lazy=True, cascade="all, delete-orphan")

    def __init__(self, original_filename, saved_filename, real_start_time, **kwargs):
        """
        function create to make sure all parameter is accepted
        """
        super(Video, self).__init__(**kwargs)
        self.original_filename = original_filename
        self.saved_filename = saved_filename
        self.real_start_time = real_start_time

    def __repr__(self):
        return f'<Video {self.id}: {self.original_filename} - {self.status}>'
    
class VehicleLog(db.Model):
    """
    Bảng log lưu lại trạng thái phương tiện theo từng timestamp.
    """
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey("video.id"), nullable=False)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.now)
    vehicle_id = db.Column(db.Integer, index=True)
    class_name = db.Column(db.String(50), nullable=False)   # car, truck, bus, ...
    speed_kmh = db.Column(db.Float, default=0.0)

    def __init__(self, video_id, timestamp, vehicle_id, class_name, speed_kmh, **kwargs):
        super(VehicleLog, self).__init__(**kwargs)
        self.video_id = video_id
        self.timestamp = timestamp
        self.vehicle_id = vehicle_id
        self.class_name = class_name
        self.speed_kmh = speed_kmh

    def __repr__(self):
        return f'<VehicleLog {self.timestamp} - Vehicle {self.vehicle_id} ({self.class_name}) {self.speed_kmh:.2f} km/h>'