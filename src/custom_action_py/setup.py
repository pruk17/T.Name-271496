from setuptools import find_packages, setup
# ros2 pkg create --build-type ament_python --license Apache-2.0 custom_action_py --dependencies rclcpp rclcpp_action
package_name = 'custom_action_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chaiyapruk',
    maintainer_email='chaiyapruk6494@gmail.com',
    description='This pkg only for "create action ndoe" practice ',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'client = custom_action_py.fibonacci_action_client:main',
            'server = custom_action_py.fibonacci_action_server:main',
        ],
    },
)
