#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import Twist
import cv2
import mediapipe as mp
import numpy as np
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

class CamTeleop(Node):
    def __init__(self):
        super().__init__('cam_teleop_node')
        # กำหนด QoS ให้ตรงกับมาตรฐานที่หุ่นยนต์ส่วนใหญ่ใช้
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE, # ลองเปลี่ยนจาก RELIABLE เป็น BEST_EFFORT
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel_command', qos_profile)
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(script_dir, 'hand_landmarker.task')
        
        if not os.path.exists(model_path):
            self.get_logger().error(f"ไม่พบไฟล์โมเดลที่: {model_path}")
            return

        base_options = python.BaseOptions(model_asset_path=model_path)
        # เพิ่ม running_mode เป็น IMAGE เพื่อให้ง่ายต่อการรันใน loop แบบนี้
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.5, # ปรับลดลงนิดหน่อยเพื่อให้จับเจอง่ายขึ้น
            min_hand_presence_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        self.cap = cv2.VideoCapture(0)
        self.get_logger().info("MediaPipe Tasks พร้อมทำงานแล้ว!")

    def run(self):
        while rclpy.ok() and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            detection_result = self.detector.detect(mp_image)
            
            linear_x = 0.0
            linear_y = 0.0
            angular_z = 0.0
            status = "WAITING"
            
            if detection_result.hand_landmarks:
                landmarks = detection_result.hand_landmarks[0]
                
                # ดึงจุดที่ต้องใช้: นิ้วโป้ง(4), นิ้วชี้(8), โคนนิ้วชี้(5), ข้อมือ(0)
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                index_base = landmarks[5]
                wrist = landmarks[0]

                # วาดจุดแค่ นิ้วโป้ง กับ นิ้วชี้ ให้ดูไม่งง
                for id in [4, 8, 5, 0]:
                    lm = landmarks[id]
                    cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 10, (255, 0, 255), -1)

                # --- ตรรกะการควบคุม ---
                
                # 1. เช็คว่าชูนิ้วชี้หรือไม่ (ปลายนิ้วชี้ต้องอยู่สูงกว่าโคนนิ้วชี้)
                if index_tip.y < index_base.y - 0.05:
                    status = "FORWARD"
                    linear_x = 0.4
                    
                    # 2. เช็คการเอียงของนิ้วชี้ (เทียบพิกัด X ระหว่างปลายกับโคน)
                    # ถ้าเอียงซ้าย/ขวา มากกว่าระยะ 0.05
                    dx = index_tip.x - index_base.x
                    
                    # 3. เช็คโหมด: ถ้ากางนิ้วโป้งออก (ดูระยะห่าง X ระหว่างโป้งกับโคนนิ้วชี้)
                    is_thumb_open = abs(thumb_tip.x - index_base.x) > 0.1
                    
                    if is_thumb_open:
                        # โหมดหมุน (Rotate)
                        if dx < -0.05:
                            status = "ROTATE LEFT"
                            angular_z = 1.0
                        elif dx > 0.05:
                            status = "ROTATE RIGHT"
                            angular_z = -1.0
                    else:
                        # โหมดสไลด์ (Slide)
                        if dx < -0.05:
                            status = "SLIDE LEFT"
                            linear_y = 0.4
                        elif dx > 0.05:
                            status = "SLIDE RIGHT"
                            linear_y = -0.4
                else:
                    status = "STOP / READY"

            # ส่งคำสั่ง
            twist = Twist()
            twist.linear.x = float(linear_x)
            twist.linear.y = float(linear_y)
            twist.angular.z = float(angular_z)
            self.publisher_.publish(twist)

            # แสดงสถานะบนหน้าจอ
            cv2.putText(frame, f"COMMAND: {status}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Index & Thumb Control', frame)
            
            if cv2.waitKey(1) == ord('q'): break

        self.cap.release()

def main():
    rclpy.init()
    node = CamTeleop()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.publisher_.publish(Twist()) # สั่งหยุดหุ่นยนต์เมื่อปิดโปรแกรม
        rclpy.shutdown()

if __name__ == '__main__':
    main()