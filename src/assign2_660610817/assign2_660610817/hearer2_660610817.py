import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Hearer2Subscriber(Node):
    def __init__(self):
        # Initialize node with name 
        super().__init__('hearer2_660610817')
        
        self.subscription = self.create_subscription(
            String,
            '/gossip_660610817',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        # Show in terminal: SUB2 get <topic>
        self.get_logger().info(f'SUB2 get /gossip_660610817: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    hearer2 = Hearer2Subscriber()
    rclpy.spin(hearer2)
    hearer2.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()