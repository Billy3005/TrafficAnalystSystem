import cv2
from datetime import datetime, timedelta
from core_analysis.VehicleDetector import VehicleDetector
from core_analysis.VehicleMonitor import VehicleMonitor

class AnalysisPipeline:
    def __init__(self, config):
        self.config = config
        self.vehicle_detector = VehicleDetector(
            model_path=config['YOLO_MODEL_PATH'],
            confidence_threshold=config['ANALYSIS_CONFIDENCE_THRESHOLD']
        )
        self.vehicle_monitor = None
    
    def _draw_results(self, frame, tracked_vehicles):

        zone_coords = self.config.get('MONITORING_ZONE')
        if zone_coords:
            x1, y1, x2, y2 = zone_coords
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            cv2.putText(frame, "Vung Giam Sat", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        for v_id, data in tracked_vehicles.items():
            draw_data = data.copy(); draw_data['id'] = v_id
            box = draw_data['box']
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
            class_name = draw_data['class_name']
            speed = draw_data.get('speed_kmh', 0.0)
            color = (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"ID:{v_id} {class_name} {int(speed)}km/h"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            y_pos = y1 - 10 if y1 - 10 > h else y1 + h + 10
            cv2.rectangle(frame, (x1, y_pos - h - 5), (x1 + w, y_pos + 5), color, -1)
            cv2.putText(frame, label, (x1, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        vehicle_count = len(tracked_vehicles)
        count_text = f"So xe trong vung: {vehicle_count}"
        cv2.putText(frame, count_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(frame, count_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
        return frame

    def run_and_yield(self, video_path, start_time, show_preview=False):
        """
        Thực thi pipeline và YIELD kết quả của từng frame một.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Lỗi: Không thể mở video tại '{video_path}'")
            return

        fps = int(cap.get(cv2.CAP_PROP_FPS)); original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        processing_width = self.config['ANALYSIS_PROCESSING_RESOLUTION_WIDTH']
        zone_coords = self.config.get('MONITORING_ZONE', [0, 0, processing_width, 0])
        zone_width_pixels = zone_coords[2] - zone_coords[0]
        pixel_per_meter = zone_width_pixels / self.config['ANALYSIS_REAL_WORLD_WIDTH_METERS']
        self.vehicle_monitor = VehicleMonitor(fps=fps, pixel_per_meter=pixel_per_meter)
        
        frame_count = 0
        if show_preview: cv2.namedWindow("Analysis Preview", cv2.WINDOW_NORMAL)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame_count += 1
            if frame_count % self.config['ANALYSIS_FRAME_SKIPPING_RATE'] != 0: continue

            aspect_ratio = original_height / original_width
            processing_height = int(processing_width * aspect_ratio)
            resized_frame = cv2.resize(frame, (processing_width, processing_height))
            
            detections = self.vehicle_detector.detect(resized_frame)
            tracked_vehicles_in_zone = self.vehicle_monitor.update(detections, resized_frame)
            current_video_time = start_time + timedelta(seconds=frame_count / fps)
            

            yield frame_count, current_video_time, tracked_vehicles_in_zone
            
            if show_preview:
                scale_w, scale_h = original_width / processing_width, original_height / processing_height
                display_vehicles = {}
                for v_id, data in tracked_vehicles_in_zone.items():
                    box = data['box']
                    orig_box = [int(box[0] * scale_w), int(box[1] * scale_h), int(box[2] * scale_w), int(box[3] * scale_h)]
                    display_vehicles[v_id] = data.copy(); display_vehicles[v_id]['box'] = orig_box
                
                frame_with_results = self._draw_results(frame, display_vehicles)
                display_frame = cv2.resize(frame_with_results, (1280, 720))
                cv2.imshow("Analysis Preview", display_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
        
        cap.release()
        if show_preview: cv2.destroyAllWindows()