from deep_sort_realtime.deepsort_tracker import DeepSort

class VehicleMonitor:
    """
    use deepsort to follow and report status(local, speed) of all vehicles was tracked
    """
    def __init__(self, fps, pixel_per_meter):
        """
        function create
            fps (int): Số khung hình trên giây của video.
            pixel_per_meter (float): Tỷ lệ pixel/mét để tính tốc độ.
        """
        self.fps = fps
        self.pixel_per_meter = pixel_per_meter
        
        # create DeepSort Tracker
        self.tracker = DeepSort(
            max_age=30, n_init=3, nms_max_overlap=1.0,
            max_cosine_distance=0.2, max_iou_distance=0.7,
            embedder="mobilenet"
        )
        
        # Dictionary to save information explore
        self.vehicle_data = {}
        
        # add speed max for suitable
        self.MAX_SPEED_KMH = 150.0

    def _get_center(self, ltrb):
        """Calculate the mind of a bounding box [l,t,r,b]."""
        return (int((ltrb[0] + ltrb[2]) / 2), int((ltrb[1] + ltrb[3]) / 2))

    def update(self, detections: list, frame: object) -> dict:
        """
        updated tracker and return a dictionary vehicle is tracking
        """
        deepsort_detections = []
        class_names = {2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'}
        for det in detections:
            x1, y1, x2, y2, cls, conf = det
            w, h = x2 - x1, y2 - y1
            class_name = class_names.get(cls, 'unknown')
            deepsort_detections.append(([x1, y1, w, h], conf, class_name))

        tracks = self.tracker.update_tracks(deepsort_detections, frame=frame)
        
        tracked_vehicles = {}

        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue

            track_id = str(track.track_id)
            ltrb = track.to_ltrb()
            current_centroid = self._get_center(ltrb)
            
            speed_kmh = 0.0
            
            if track_id in self.vehicle_data and 'centroid' in self.vehicle_data[track_id]:
                prev_centroid = self.vehicle_data[track_id]['centroid']
                distance_pixels = ((current_centroid[0] - prev_centroid[0]) ** 2 + 
                                   (current_centroid[1] - prev_centroid[1]) ** 2) ** 0.5
                
                if self.pixel_per_meter > 0 and self.fps > 0:
                    speed_pixel_per_second = distance_pixels * self.fps
                    speed_meter_per_second = speed_pixel_per_second / self.pixel_per_meter
                    calculated_speed_kmh = speed_meter_per_second * 3.6
                    
                    if calculated_speed_kmh < self.MAX_SPEED_KMH:
                        speed_kmh = calculated_speed_kmh
            
            self.vehicle_data[track_id] = {
                'box': [int(c) for c in ltrb],
                'class_name': track.get_det_class(),
                'speed_kmh': speed_kmh,
                'centroid': current_centroid
            }
            tracked_vehicles[track_id] = self.vehicle_data[track_id]
        
        tracked_ids = {str(t.track_id) for t in tracks}
        for track_id in list(self.vehicle_data.keys()):
            if track_id not in tracked_ids:
                del self.vehicle_data[track_id]
                
        return tracked_vehicles