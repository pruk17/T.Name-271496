import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np

class LidarSubscriber(Node):
    def __init__(self):
        super().__init__('lidar_subscriber_node')
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        # 1. Get the total number of readings in one scan cycle
        num_readings = len(msg.ranges)
        
        # 2. Calculate the index for 0 degrees
        # Typically in rplidar_ros, 0 degrees is at the middle index of the array
        mid_idx = num_readings // 2
        
        # 3. Calculate the index range for ± 5 degrees
        # Determine how many radians each index represents
        angle_increment = msg.angle_increment
        five_deg_in_rad = np.deg2rad(5)
        index_offset = int(five_deg_in_rad / angle_increment)
        
        # 4. Extract the data slice for 0 ± 5 degrees
        # Prevent index out of bounds
        start_idx = max(0, mid_idx - index_offset)
        end_idx = min(num_readings, mid_idx + index_offset)
        
        target_ranges = msg.ranges[start_idx:end_idx]
        
        # 5. Delete Infinity and 0 values before calculation
        valid_ranges = [r for r in target_ranges if np.isfinite(r) and r > msg.range_min]
        
        if valid_ranges:
            avg_distance = sum(valid_ranges) / len(valid_ranges)
            self.get_logger().info(f'Average Distance at 0±5°: {avg_distance:.3f} m (Points: {len(valid_ranges)})')
        else:
            self.get_logger().warn('No valid data in 0±5° range')

def main(args=None):
    rclpy.init(args=args)
    node = LidarSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()