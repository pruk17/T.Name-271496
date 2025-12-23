from setuptools import find_packages, setup

package_name = 'assign2_660610817'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    
    install_requires=['setuptools',
                      'rclpy',      # Essential for ROS2 Python
                      'std_msgs',   # Essential for String messages
                      'rcl_interfaces',
    ],
    zip_safe=True,
    maintainer='chaiyapruk',
    maintainer_email='chaiyapruk6494@gmail.com',
    description='Assignment 2 for 271496',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'talker = assign2_660610817.whisper_660610817:main',
            'listener1 = assign2_660610817.hearer1_660610817:main',
            'listener2 = assign2_660610817.hearer2_660610817:main',
        ],
    },
)
