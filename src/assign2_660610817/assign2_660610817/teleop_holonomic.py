#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

# การตั้งค่าปุ่มกด
msg = """
Holonomic Teleop for myAGV
---------------------------
Moving around:
   q    w    e
   a    s    d
   z    x    c

w/x : forward/backward (linear x)
a/d : left/right       (linear y)
q/e : rotate L/R       (angular z)
s   : Stop

CTRL-C to quit
"""

moveBindings = {
    'w': (1, 0, 0),  'x': (-1, 0, 0),
    'a': (0, 1, 0),  'd': (0, -1, 0),
    'q': (0, 0, 1),  'e': (0, 0, -1),
    's': (0, 0, 0),
}

class TeleopHolonomic(Node):
    def __init__(self):
        super().__init__('teleop_keyboard_node')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel_command', 10)
        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info("Teleop Node Started. Use keys to move.")

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        print(msg)
        linear_x = 0.0
        linear_y = 0.0
        angular_z = 0.0
        
        try:
            while True:
                key = self.get_key()
                if key in moveBindings.keys():
                    lx, ly, az = moveBindings[key]
                    # adjust speed( EX. 0.2 m/s , 0.5 rad/s)
                    linear_x = lx * 0.4
                    linear_y = ly * 0.4
                    angular_z = az * 0.5
                    
                    if key == 's':
                        linear_x = linear_y = angular_z = 0.0
                elif key == '\x03': # CTRL+C
                    break
                
                twist = Twist()
                twist.linear.x = float(linear_x)
                twist.linear.y = float(linear_y)
                twist.angular.z = float(angular_z)
                self.publisher_.publish(twist)
                

        except Exception as e:
            print(e)
        finally:
            twist = Twist()
            self.publisher_.publish(twist)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

def main():
    rclpy.init()
    node = TeleopHolonomic()
    node.run()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
