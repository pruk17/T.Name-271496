from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    who_arg = DeclareLaunchArgument('who', default_value='myROS')
    speaker_arg = DeclareLaunchArgument('speaker', default_value='say')
    msg_arg = DeclareLaunchArgument('spk_msg', default_value=' y so EZ')
    return LaunchDescription([
        who_arg,
        speaker_arg,
        msg_arg,
        Node(
            package='assign2_660610817',
            namespace='whisper',
            executable='talker',
            name='Talker',
            # 2. Use LaunchConfiguration to 'grab' the value from the terminal
            parameters=[{
                'who': LaunchConfiguration('who'),
                'speaker': LaunchConfiguration('speaker'),
                'spk_msg': LaunchConfiguration('spk_msg'),
            }],
            # Using remappings for the topic is cleaner than 'arguments'
            remappings=[('/gossip_660610817', '/assignment5')]
        ),
        # Node(
        #     package='assign2_660610817',
        #     namespace='whisper',
        #     executable='talker',
        #     name='Talker',
        #     arguments=['--ros-args','-r','/gossip_660610817:=/assignment5',
        #                                 '-p','who:=myROS',
        #                                 '-p','speaker:=say',
        #                                 '-p','spk_msg:=" y so EZ"'],
        # ),
        Node(
            package='assign2_660610817',
            namespace='hearer1',
            executable='listener1',
            name='Hearer_1',
            remappings=[('/gossip_660610817', '/assignment5')]
        ),
        #     arguments=['--ros-args','-r','/gossip_660610817:=/assignment5'],
        # ),
        Node(
            package='assign2_660610817',
            namespace='hearer2',
            executable='listener2',
            name='Hearer_2',
            remappings=[('/gossip_660610817', '/assignment5')]
        )
        #     arguments=['--ros-args','-r','/gossip_660610817:=/assignment5'],
        # ),
    ])