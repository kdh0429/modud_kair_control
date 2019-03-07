#!/usr/bin/env python
# ROS Imports
import rospy
from math import pi
from std_msgs.msg import Float64
from sensor_msgs.msg import JointState

Deg2Rad = pi/180
q_init =[0.0, 0.0, 0.0, 0.0]
is_q_init = False

def cubic(time, time_0, time_f, x_0, x_f, x_dot_0, x_dot_f):
    x_t = 0.0

    if (time < time_0):
        x_t = x_0
    elif (time > time_f):
        x_t = x_f
    else:
        
        elapsed_time = time - time_0
        total_time = time_f - time_0
        total_time2 = total_time * total_time
        total_time3 = total_time2 * total_time2
        total_x   = x_f - x_0

        x_t = x_0 + x_dot_0 * elapsed_time + (3 * total_x / total_time2 - 2 * x_dot_0 / total_time - x_dot_f / total_time)* elapsed_time * elapsed_time + (-2 * total_x / total_time3 + (x_dot_0 + x_dot_f) / total_time2) * elapsed_time * elapsed_time * elapsed_time

    return x_t

def joint_states_cb(joint_states):
    global is_q_init
    if  is_q_init == False:
        i=0
        while i<4:
            q_init[i] = joint_states.position[i+2]
            i += 1
        is_q_init = True

def main():
    rospy.init_node('joint_space_publisher')
    
    joint_states_sub = rospy.Subscriber('/open_manipulator/joint_states', JointState, joint_states_cb)
    joint1_command_pub = rospy.Publisher('/open_manipulator/joint1_position/command', Float64, queue_size=3)
    joint2_command_pub = rospy.Publisher('/open_manipulator/joint2_position/command', Float64, queue_size=3)
    joint3_command_pub = rospy.Publisher('/open_manipulator/joint3_position/command', Float64, queue_size=3)
    joint4_command_pub = rospy.Publisher('/open_manipulator/joint4_position/command', Float64, queue_size=3)


    rate = rospy.Rate(100)

    j1_target, j2_target, j3_target, j4_target = [float(j_command) for j_command in raw_input("Type 4 Joint Target Position(degree):").split()]
    j1_target = j1_target*Deg2Rad
    j2_target = j2_target*Deg2Rad
    j3_target = j3_target*Deg2Rad
    j4_target = j4_target*Deg2Rad
    
    time_init = rospy.get_time()
    while not rospy.is_shutdown():
        time = rospy.get_time()
        j1 = cubic(time, time_init, time_init+3.0, q_init[0], j1_target, 0.0, 0.0)
        j2 = cubic(time, time_init, time_init+3.0, q_init[1], j2_target, 0.0, 0.0)
        j3 = cubic(time, time_init, time_init+3.0, q_init[2], j3_target, 0.0, 0.0)
        j4 = cubic(time, time_init, time_init+3.0, q_init[3], j4_target, 0.0, 0.0)
        print(j4)
        joint1_command_pub.publish(j1)
        joint2_command_pub.publish(j2)
        joint3_command_pub.publish(j3)
        joint4_command_pub.publish(j4)
        rate.sleep()

        
if __name__ == '__main__':
    try:    
        main()
    except rospy.ROSInterruptException:
                pass
