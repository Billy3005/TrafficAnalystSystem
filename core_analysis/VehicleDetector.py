import torch
import numpy as np
import cv2
import os

class VehicleDetector:
    """
    tracking car used yolov5 model
    """
    def __init__(self, model_path, confidence_threshold=0.4, iou_threshold=0.5):
        """
        function create, run for install yolov5
        model will be install one time when object is created
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.allowed_classes = [2, 3, 5, 7] # car, motorcycle, bus, truck

        try:
            # url for folders of yolov5 
            yolo_repo_path = os.path.join(os.path.dirname(model_path), 'yolov5')

            # check resources yes or no
            if not os.path.isdir(yolo_repo_path) or not os.path.exists(self.model_path):
                 raise FileNotFoundError("Không tìm thấy tài nguyên cục bộ cho YOLOv5.")

            # save mode from local
            self.model = torch.hub.load(
                repo_or_dir=yolo_repo_path,
                model='custom',
                path=self.model_path,
                source='local' 
            )

            # Config parameter for model
            self.model.conf = self.confidence_threshold
            self.model.iou = self.iou_threshold

            print("Mô hình VehicleDetector (YOLOv5) đã được khởi tạo thành công từ nguồn LOCAL.")

        except Exception as e:
            print(f"Lỗi nghiêm trọng khi tải mô hình YOLOv5 từ nguồn local: {e}")
            print("\nHãy chắc chắn rằng bạn đã thực hiện đúng các bước sau:")
            print(f"1. Tải file trọng số (ví dụ: 'yolov5s.pt') vào thư mục chứa models.")
            print(f"2. Clone toàn bộ repository 'ultralytics/yolov5' vào cùng thư mục đó.")
            raise

    def detect(self, frame: np.ndarray) -> list:
        """
        Phát hiện phương tiện trong một khung hình video.

        Args:
            frame (np.ndarray): Khung hình đầu vào từ OpenCV (định dạng BGR).

        Returns:
            list: Một danh sách các phát hiện. Mỗi phát hiện là một list
                  chứa [x1, y1, x2, y2, class_id, confidence_score].
        """
        # YOLOv5 required photo at form RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # perform tracking
        results = self.model(rgb_frame)

        # take information from result
        detections = results.xyxy[0].cpu().numpy()

        # filter tracks base on class is accepted 
        filtered_detections = []
        for det in detections:
            x1, y1, x2, y2, conf, cls = det
            if int(cls) in self.allowed_classes:
                filtered_detections.append([int(x1), int(y1), int(x2), int(y2), int(cls), float(conf)])
        
        return filtered_detections