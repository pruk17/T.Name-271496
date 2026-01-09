from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # 1. run node Driver of RPLIDAR A1
        Node(
            package='rplidar_ros',
            executable='rplidar_node',
            name='rplidar_node',
            parameters=[{
                'serial_port': '/dev/ttyUSB0',
                'serial_baudrate': 115200,
                'frame_id': 'laser_frame',
                'inverted': False,
                'angle_compensate': True,
            }],
            output='screen'
        ),

        Node(
            package='pruk_lidar_a1',
            executable='ld_read',
            name='lidar_reader',
            output='screen'
        )
    ])