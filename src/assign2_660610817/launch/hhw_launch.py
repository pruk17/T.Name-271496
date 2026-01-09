from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='assign2_660610817',
            namespace='whisper',
            executable='talker',
            name='Talker',
            arguments=['--ros-args','-r','/gossip_660610817:=/assignment5',
                                        '-p','who:=myROS',
                                        '-p','speaker:=say',
                                        '-p','spk_msg:=" y so EZ"'],
        ),
        Node(
            package='assign2_660610817',
            namespace='hearer1',
            executable='listener1',
            name='Hearer_1',
            arguments=['--ros-args','-r','/gossip_660610817:=/assignment5'],
        ),
        Node(
            package='assign2_660610817',
            namespace='hearer2',
            executable='listener2',
            name='Hearer_2',
            arguments=['--ros-args','-r','/gossip_660610817:=/assignment5'],
        ),
    ])