from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'pruk_lidar_a1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools',
                      'rclpy',      # ROS2 Python
                      'rcl_interfaces',
                      ],
    zip_safe=True,
    maintainer='chaiyapruk',
    maintainer_email='chaiyapruk6494@gmail.com',
    description='get the value from lidar A1 scanning and find length on angle 0 +- 5 degree',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'ld_read = pruk_lidar_a1.lidar_reader:main', 
        ],
    },
)
