import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Hearer1Subscriber(Node):
    def __init__(self):
        # Initialize node with name 
        super().__init__('hearer1_660610817')
        
        # Create subscription to topic '/__'
        self.subscription = self.create_subscription(
            String,
            '/gossip_660610817',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        # Show in terminal: SUB1 get <topic>
        self.get_logger().info(f'SUB1 get: "{self.subscription.topic_name}" "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    hearer1 = Hearer1Subscriber()
    rclpy.spin(hearer1)
    hearer1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()