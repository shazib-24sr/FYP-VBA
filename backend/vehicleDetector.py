import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
import os
from shapely.geometry import LineString, box
from vehicleTracker import VehicleTracker
import subprocess

class VehicleDetector:
    def __init__(self, model_path,plate_model_path, video_path, output_path="output.mp4", csv_path="detections.csv", resolution=(640, 480), frame_skip=1,line1=None, line2=None, box_points=None):
        self.model = YOLO(model_path)
        self.violation_frames_dir = "violations"
        os.makedirs(self.violation_frames_dir, exist_ok=True)
        
        self.video_path = video_path
        self.output_path = output_path
        self.csv_path = csv_path
        self.detection_data = []
        self.resolution = resolution
        self.frame_skip = frame_skip
        self.plate_model = YOLO(plate_model_path)
        
        self.tracker = VehicleTracker()
        self.vehicle_positions = {}
        self.wrong_way_vehicles = {} 
        self.line1_start, self.line1_end = line1 if line1 else  ((600, 643), (1005, 1015))
        self.line2_start, self.line2_end = line2 if line2 else  ((952, 696), (1899,874))
            
        self.box_points = box_points if box_points is not None else \
                          np.array([(532,633), (611,1060), (1899,874), (709,647)], dtype=np.int32)
      

    def is_point_inside_box(self, point, box_points):
        """Check if the point (center of the vehicle) is inside the polygon (the box)."""
       
        box = box_points.reshape((-1, 1, 2))
        return cv2.pointPolygonTest(box, point, False) >= 0
    
    
   
    
    def assign_vehicle_id(self, center_x, center_y):
        return self.tracker.update(center_x, center_y)
    
    def get_unit_vector(self,start, end):
        vector = np.array(end) - np.array(start)
        return vector / np.linalg.norm(vector)
    
    def detect_plate_text(self, frame, bbox):
        x1, y1, x2, y2 = bbox
        plate_img = frame[y1:y2, x1:x2]
        if plate_img.size == 0:
            return ""

        # OCR read
        result = self.reader.readtext(plate_img)
        if result:
            # Concatenate all text parts
            text = "".join([res[1] for res in result])
            return text.strip()
        return ""

    def calculate_speed(self,  vehicle_id, center_x, center_y, fps, tracker):
        speed_kmph = 0.0
        direction = "unknown"
        distance_meters = 0.0
        time_seconds = 0.0
        trajectory = self.tracker.get_trajectory(vehicle_id)

        if len(trajectory) >= 2:
            start_point = np.array(trajectory[0])
            end_point = np.array(trajectory[-1])

            movement_vector = end_point - start_point
            movement_distance = np.linalg.norm(movement_vector)

            if movement_distance > 1e-3:
                movement_unit_vector = movement_vector / movement_distance
                lane1_vector = self.get_unit_vector([582, 641], [915, 993])
                lane2_vector = self.get_unit_vector([1078, 571], [1597, 693])

                dot1 = np.dot(movement_unit_vector, lane1_vector)
                dot2 = np.dot(movement_unit_vector, lane2_vector)

                if dot1 > 0.5 or dot2 > 0.5:
                    direction = "right way"
                elif dot1 < -0.5 or dot2 < -0.5:
                    direction = "wrong way"
                else:
                    direction = "unclear"

                distance_meters = movement_distance * 0.0264  
                time_seconds = len(trajectory) / fps
                if time_seconds > 0:
                    speed_kmph = (distance_meters / time_seconds) * 3.6

        return speed_kmph, distance_meters, time_seconds, direction

    
   
    def line_intersects_bbox(self, line_start, line_end, bbox):
        

        x1, y1, x2, y2 = bbox
        bbox_shape = box(x1, y1, x2, y2)
        line_shape = LineString([line_start, line_end])
        return bbox_shape.intersects(line_shape)
   

   

    def process_frame(self, frame, frame_count, fps):
        # frame = cv2.rotate(frame, cv2.ROTATE_180)  
        results = self.model(frame)  

        detections = results[0].boxes.data.cpu().numpy()
        

        cv2.line(frame, self.line1_start, self.line1_end, (255, 0, 0), 2)
        cv2.line(frame, self.line2_start, self.line2_end, (255, 0, 0), 2)

        

        for detection in detections:
            x1, y1, x2, y2, confidence, class_id = detection
            confidence = float(confidence)
            # plate_results = self.plate_model(frame)   
            if confidence >= 0.7:
                label = self.model.names[int(class_id)]
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2

                if not self.is_point_inside_box((center_x, center_y), self.box_points):
                    continue

                vehicle_id, plate_number = self.tracker.update(center_x, center_y, frame_count)
                
                speed_kmph, distance_meters, time_seconds, direction = self.calculate_speed(vehicle_id, center_x, center_y, fps, self.tracker)
                bbox = (int(x1), int(y1), int(x2), int(y2))
                touches_line1 = self.line_intersects_bbox(self.line1_start, self.line1_end, bbox)
                touches_line2 = self.line_intersects_bbox(self.line2_start, self.line2_end, bbox)
                lane_status = "unknown"
                if touches_line1 or touches_line2:
                    lane_status = "normal lane"
                elif not touches_line1 and not touches_line2:
                    lane_status = "abrupt lane change"
                
                
                speed_limit = 120  

                # Check for violations
                is_overspeeding = speed_kmph > speed_limit
                is_wrong_way = direction == "wrong way"
                is_lane_change = lane_status == "abrupt lane change"

                if is_overspeeding:
                    violation_type = "overspeeding"
                elif is_wrong_way:
                    violation_type = "wrongway"
                elif is_lane_change:
                    violation_type = "abruptLaneChange"
                else:
                    violation_type = None

                if violation_type:
                    violation_dir = os.path.join(self.violation_frames_dir, violation_type)
                    os.makedirs(violation_dir, exist_ok=True)
                    violation_filename = f"{vehicle_id}_frame_{frame_count}_{violation_type}.jpg"
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)  
                    cv2.putText(frame, f"{violation_type.upper()} - ID: {vehicle_id}", 
                                (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    path = os.path.join(violation_dir, violation_filename)
                    cv2.imwrite(path, frame)

                


                self.detection_data.append({
                    "vehicle_id": vehicle_id,
                    "class": label,
                    "confidence": confidence,
                    "x1": int(x1),
                    "y1": int(y1),
                    "x2": int(x2),
                    "y2": int(y2),
                    "plate_number": plate_number,
                    "speed_kmph": speed_kmph,
                    "distance_meters": distance_meters,
                    "time_seconds": time_seconds,
                    "direction": direction,
                    "lane_status": lane_status
                    
                    
                })

                # Draw bounding box for vehicle
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"ID: {vehicle_id}, Plate: {plate_number}", 
                            (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame


    
    def save_detections_to_csv(self):
        df = pd.DataFrame(self.detection_data)
        df.to_csv(self.csv_path, index=False)
        print(f"Detections saved to {self.csv_path}")
        
    

       
    def process_video(self, output_path):
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error: Unable to open video.")
            return

       
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        print(f"fps: {fps}")
        output_width, output_height = self.resolution

       
        # fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        # out = cv2.VideoWriter(self.output_path, fourcc, fps, (output_width, output_height))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can also use 'MJPG', 'MP4V', etc.
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (output_width, output_height))
        frame_count = 0

    
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

          

            processed_frame = self.process_frame(frame, frame_count, fps)
            resized_frame = cv2.resize(processed_frame, (output_width, output_height))
            out.write(resized_frame)
            
          
           

            
            print(f"Frame processed: {frame_count}")
            print(f"fps frame : {fps}")

            frame_count += 1

        cap.release()
        out.release()
        
        self.save_detections_to_csv()
        
        