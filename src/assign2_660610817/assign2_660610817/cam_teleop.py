#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
import cv2
import mediapipe as mp
import numpy as np
import os
import math

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class CamTeleop(Node):
    def __init__(self):
        super().__init__('cam_teleop_node')
        
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=5
        )
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel_command', qos_profile)
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(script_dir, 'hand_landmarker.task')
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.8,
            min_hand_presence_confidence=0.8
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        self.cap = cv2.VideoCapture(0)
        
        # --- ตัวแปรสำหรับกรองสัญญาณ (Filtering) ---
        self.smooth_thumb_dist = 0.0
        self.smooth_dx = 0.0
        self.alpha = 0.5  # ค่าความสมูท (0.1 = นิ่งมากแต่ช้า, 0.9 = ไวแต่สั่น)
        self.stop_counter = 0
        
        self.get_logger().info("Mecanum Control V5: Advanced Filtering Active!")

    def run(self):
        while rclpy.ok() and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            detection_result = self.detector.detect(mp_image)
            
            linear_x, linear_y, angular_z = 0.0, 0.0, 0.0
            status = "STOP / NO HAND"
            color = (0, 0, 255)
            
            if detection_result.hand_landmarks and detection_result.handedness:
                hand_label = detection_result.handedness[0][0].category_name
                
                if hand_label == "Right": # ตรวจจับมือซ้าย
                    landmarks = detection_result.hand_landmarks[0]
                    
                    # พิกัดจุดสำคัญ
                    thumb_tip = landmarks[4]
                    index_mcp = landmarks[5]
                    index_tip = landmarks[8]
                    middle_mcp = landmarks[9]

                    # 1. คำนวณค่าสด
                    raw_thumb_dist = math.sqrt((thumb_tip.x - index_mcp.x)**2 + (thumb_tip.y - index_mcp.y)**2)
                    raw_dx = index_tip.x - index_mcp.x

                    # 2. กรองสัญญาณ (EMA Filter)
                    self.smooth_thumb_dist = (self.alpha * raw_thumb_dist) + ((1 - self.alpha) * self.smooth_thumb_dist)
                    self.smooth_dx = (self.alpha * raw_dx) + ((1 - self.alpha) * self.smooth_dx)

                    # 3. กำหนด Thresholds (ใช้ค่าที่กรองแล้ว)
                    is_index_up = index_tip.y < index_mcp.y - 0.08
                    is_thumb_open = self.smooth_thumb_dist > 0.10 # ปรับเพิ่มความกว้างป้องกันการแกว่ง
                    
                    # 4. ลำดับการตัดสินใจ (Logic)
                    if is_index_up:
                        if is_thumb_open:
                            # โหมด ROTATE: ล็อกไว้ไม่ให้เข้า Slide
                            linear_x = 0.2
                            if self.smooth_dx < -0.04:
                                status, angular_z = "ROTATE LEFT", 1.0
                            elif self.smooth_dx > 0.04:
                                status, angular_z = "ROTATE RIGHT", -1.0
                            else:
                                status = "FORWARD (READY TO ROTATE)"
                        else:
                            # โหมด SLIDE: เฉพาะตอนหุบนิ้วโป้ง
                            linear_x = 0.4
                            if self.smooth_dx < -0.05:
                                status, linear_y = "SLIDE LEFT", 0.4
                            elif self.smooth_dx > 0.05:
                                status, linear_y = "SLIDE RIGHT", -0.4
                            else:
                                status = "FORWARD"
                        color = (0, 255, 0)

                    elif is_thumb_open:
                        # ถอยหลัง: กางโป้ง + นิ้วชี้ต้องไม่ชู
                        if index_tip.y > index_mcp.y - 0.06:
                            linear_x = -0.4
                            status = "REVERSE"
                            color = (255, 0, 255)

                    # --- Drawing Feedback ---
                    # วาดเส้นเชื่อม Thumb กับ Index MCP เพื่อดูระยะห่าง
                    pt1 = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                    pt2 = (int(index_mcp.x * w), int(index_mcp.y * h))
                    cv2.line(frame, pt1, pt2, (255, 255, 0), 2)
                    cv2.circle(frame, pt1, 8, (255, 0, 255), -1)
                    cv2.circle(frame, pt2, 8, (255, 255, 255), -1)
                    cv2.circle(frame, (int(index_tip.x * w), int(index_tip.y * h)), 8, (0, 255, 0), -1)

            # Publish คำสั่ง Twist
            msg = Twist()
            msg.linear.x, msg.linear.y, msg.angular.z = float(linear_x), float(linear_y), float(angular_z)
            self.publisher_.publish(msg)

            # GUI แสดงผล
            cv2.rectangle(frame, (0, 0), (450, 110), (30, 30, 30), -1)
            cv2.putText(frame, f"STATUS: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            cv2.putText(frame, f"Smooth Thumb Dist: {self.smooth_thumb_dist:.3f}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            cv2.putText(frame, f"Smooth Index dX: {self.smooth_dx:.3f}", (20, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            cv2.imshow('Mecanum Control V5 (Filtered)', frame)
            if cv2.waitKey(1) == ord('q'): break

        self.cap.release()
        cv2.destroyAllWindows()

def main():
    rclpy.init()
    node = CamTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher_.publish(Twist())
        rclpy.shutdown()

if __name__ == '__main__':
    main()