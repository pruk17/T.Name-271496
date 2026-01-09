import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rcl_interfaces.msg import ParameterDescriptor

#ros2 run rqt_reconfigure rqt_reconfigure (use to see the parameter of nodes and adjust it)

class WhisperPublisher(Node):
    def __init__(self):
        # Initialize node with name 
        super().__init__('whisper_660610817')
        who_descriptor = ParameterDescriptor(description='speaker name')
        speaker_descriptor = ParameterDescriptor(description='behavior')
        spk_msg_descriptor = ParameterDescriptor(description='Msg')

        # who => ID key , Pruk => default value, who_descriptor => metadata ( help msg)
        self.declare_parameter('who', 'Pruk', who_descriptor)
        self.declare_parameter('speaker', 'shoutout', speaker_descriptor)
        self.declare_parameter('spk_msg', 'Successful assignment', spk_msg_descriptor)

        # Create publisher for topic '/___' with String type
        self.publisher_ = self.create_publisher(String, '/gossip_660610817', 10)

        # Set timer period (e.g., every 1 second)
        timer_period = 1.0  
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0 # Initial value

    def timer_callback(self):
        who = self.get_parameter('who').get_parameter_value().string_value
        speaker = self.get_parameter('speaker').get_parameter_value().string_value
        spk_msg = self.get_parameter('spk_msg').get_parameter_value().string_value

        log_msg = f'{who} {speaker} {spk_msg} {self.i}'
        self.get_logger().info(log_msg)

        msg = String()
        msg.data = log_msg
        self.publisher_.publish(msg)
        
        self.i += 1

def main(args=None):
    rclpy.init(args=args)
    whisper_publisher = WhisperPublisher()
    rclpy.spin(whisper_publisher)
    whisper_publisher.destroy_node()
    rclpy.init()
if __name__ == '__main__':
    main()



#---------------------------------  ASSIGNMENT 2 (OLD) ----------------------------------------

# import rclpy
# from rclpy.node import Node
# from std_msgs.msg import String

# class WhisperPublisher(Node):
#     def __init__(self):
#         # Initialize node with name 
#         super().__init__('whisper_660610817')
        
#         # Create publisher for topic '/___' with String type
#         self.publisher_ = self.create_publisher(String, '/gossip_660610817', 10)
        
#         # Set timer period (e.g., every 1 second)
#         timer_period = 1.0  
#         self.timer = self.create_timer(timer_period, self.timer_callback)
#         self.i = 0 # Initial value

#     def timer_callback(self):
#         msg = String()
#         # Message pattern: "Oh My ROS, I am : <i+=2>"
#         msg.data = f'Oh My ROS, I am 660610817: {self.i}'
#         self.publisher_.publish(msg)
        
#         # Show in terminal: PUB whisper <topic>
#         self.get_logger().info(f'PUB whisper /gossip_660610817: "{msg.data}"')
        
#         # Increment i by 2
#         self.i += 2

# def main(args=None):
#     rclpy.init(args=args)
#     whisper_publisher = WhisperPublisher()
#     rclpy.spin(whisper_publisher)
#     whisper_publisher.destroy_node()
#     rclpy.init()

# if __name__ == '__main__':
#     main()