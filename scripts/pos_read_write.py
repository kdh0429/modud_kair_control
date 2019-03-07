#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dynamixel_sdk import * 
from math import pi
import numpy as np
# ROS Imports
import rospy
from std_msgs.msg import Float64MultiArray
from sensor_msgs.msg import JointState

Deg2Rad = pi/180
Rad2Deg = 1/Deg2Rad

### TO DO : Change Control Table to XM430-W350 spec ###
DXL_Resolution = 0.088 # In degree
DXL_VELOCITY_RESOLUTION = 0.229 # In rpm # For XM430-W210 0.229
RPM2Rad = 2*pi/60


# Control table address
ADDR_TORQUE_ENABLE      = 64                 # ADDR_TORQUE_ENABLE = 64
ADDR_PRESENT_POSITION   = 132                 # ADDR_TORQUE_ENABLE = 132
ADDR_PRESENT_VELOCITY   = 128                 # ADDR_TORQUE_ENABLE = 128
ADDR_OP_MODE = 11
#ADDR_CW_LIMIT      = 6                       # No need, Instead ADDR_OP_MODE = 11
#ADDR_CCW_LIMIT      = 8                      # No need
ADDR_GOAL_POSITION = 116                      # ADDR_GOAL_POSITION = 116
# Data Byte Length
LEN_GOAL_POSITION       = 4
LEN_PRESENT_POSITION    = 4                 # 4
LEN_PRESENT_VELOCITY    = 4                 # 4


CCW_LIMIT = 1048575
# Protocol version
PROTOCOL_VERSION            = 2.0               

# Default setting
DXL1_ID                     = 11                 
DXL2_ID                     = 12                 
DXL3_ID                     = 13
DXL4_ID                     = 14
BAUDRATE                    = 1000000             
DEVICENAME                  = '/dev/ttyUSB2'    
                                               

TORQUE_ENABLE               = 1                
TORQUE_DISABLE              = 0                


class DynamixelPositionControl(object):
    def __init__(self):
        # Dynamixel Setting
        rospy.loginfo("Dynamixel Position Controller Created")
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        self.groupSyncWrite = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_GOAL_POSITION, LEN_GOAL_POSITION)
        ### TO DO : Uncomment below ###
        self.groupBulkReadPosition = GroupBulkRead(self.portHandler, self.packetHandler)
        self.groupBulkReadVelocity = GroupBulkRead(self.portHandler, self.packetHandler)
        # Port Open
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            quit()
        # Set Multi Turn Mode
        ### TO DO : XM430-W350 supports Operating Mode(11) Change its value to 3(position control) or 1(velocity control) ###
        ### TO DO : Uncomment 1,2,3,4 ###
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL1_ID, ADDR_OP_MODE, 4)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL2_ID, ADDR_OP_MODE, 4)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL3_ID, ADDR_OP_MODE, 4)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL4_ID, ADDR_OP_MODE, 4)

        ### TO DO : Uncomment below ###
        dxl_addparam_result = self.groupBulkReadPosition.addParam(DXL1_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        dxl_addparam_result = self.groupBulkReadPosition.addParam(DXL2_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        dxl_addparam_result = self.groupBulkReadPosition.addParam(DXL3_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        dxl_addparam_result = self.groupBulkReadPosition.addParam(DXL4_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        dxl_addparam_result = self.groupBulkReadVelocity.addParam(DXL1_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        dxl_addparam_result = self.groupBulkReadVelocity.addParam(DXL2_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        dxl_addparam_result = self.groupBulkReadVelocity.addParam(DXL3_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        dxl_addparam_result = self.groupBulkReadVelocity.addParam(DXL4_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)

        # Enable Dynamixel Torque
        ### TO DO : Uncomment DXL 3 and 4 ###
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL1_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        self.error_check(dxl_comm_result, dxl_error)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL2_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        self.error_check(dxl_comm_result, dxl_error)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL3_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, DXL4_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)

        
        # ROS Publisher
        self.joint_states_pub = rospy.Publisher('/open_manipulator/joint_states', JointState, queue_size=3)
        self.joint_states_pub_tmp = rospy.Publisher('/open_manipulator/joint_states_tmp', JointState, queue_size=3)
        # ROS Subcriber
        self.joint_pos_command_sub = rospy.Subscriber('/open_manipulator/joint_position/command', Float64MultiArray, self.joint_command_cb)
        
        self.dxl_present_position = np.zeros(4)
        self.dxl_present_velocity = np.zeros(4)
        self.q_desired = np.zeros(4)
        self.dxl_goal_position = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.read_dxl()
        for i in range(4):
            self.dxl_goal_position[i] = [DXL_LOBYTE(DXL_LOWORD(self.dxl_present_position[i])), DXL_HIBYTE(DXL_LOWORD(self.dxl_present_position[i])),\
                                         DXL_LOBYTE(DXL_HIWORD(self.dxl_present_position[i])), DXL_HIBYTE(DXL_HIWORD(self.dxl_present_position[i]))]

        self.joint_states = JointState()
        self.r = rospy.Rate(100)
        while not rospy.is_shutdown():
            self.read_dxl()
            self.write_dxl()
            self.r.sleep()
    
    def joint_command_cb(self, joint_desired):
        i=0
        while i<4:
            self.q_desired[i] = joint_desired.data[i]
            dxl_command = int(self.q_desired[i]* Rad2Deg / DXL_Resolution)
            if (dxl_command < 0):
                dxl_command = dxl_command + 2**(8*LEN_PRESENT_POSITION)
            self.dxl_goal_position[i] = [DXL_LOBYTE(DXL_LOWORD(dxl_command)), DXL_HIBYTE(DXL_LOWORD(dxl_command)),\
                                         DXL_LOBYTE(DXL_HIWORD(dxl_command)), DXL_HIBYTE(DXL_HIWORD(dxl_command))]
            i += 1

    def read_dxl(self):
        ### TO DO : Uncomment below ###
        dxl_comm_result = self.groupBulkReadPosition.txRxPacket()

        self.dxl_present_position[0] = self.groupBulkReadPosition.getData(DXL1_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        self.dxl_present_position[1] = self.groupBulkReadPosition.getData(DXL2_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        self.dxl_present_position[2] = self.groupBulkReadPosition.getData(DXL3_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        self.dxl_present_position[3] = self.groupBulkReadPosition.getData(DXL4_ID, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        self.dxl_comm_result = self.groupBulkReadVelocity.txRxPacket()
        self.dxl_present_velocity[0] = self.groupBulkReadVelocity.getData(DXL1_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        self.dxl_present_velocity[1] = self.groupBulkReadVelocity.getData(DXL2_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        self.dxl_present_velocity[2] = self.groupBulkReadVelocity.getData(DXL3_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        self.dxl_present_velocity[3] = self.groupBulkReadVelocity.getData(DXL4_ID, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        for i in range(4):
            if(self.dxl_present_position[i] > CCW_LIMIT):
                self.dxl_present_position[i] -= 2**(8*LEN_PRESENT_POSITION)
        
        ### TO DO : Change 3rd and 4th value to dxl3 and dxl4 position ###
        q_current = [0.0, 0.0, self.dxl_present_position[0]*DXL_Resolution * Deg2Rad, self.dxl_present_position[1]*DXL_Resolution * Deg2Rad, \
                    self.dxl_present_position[2]*DXL_Resolution * Deg2Rad, self.dxl_present_position[3]*DXL_Resolution * Deg2Rad]
        qdot_current = [0.0, 0.0, self.dxl_present_velocity[0]*DXL_VELOCITY_RESOLUTION * RPM2Rad, self.dxl_present_velocity[1]*DXL_VELOCITY_RESOLUTION * RPM2Rad,\
                    self.dxl_present_velocity[2]*DXL_VELOCITY_RESOLUTION * RPM2Rad, self.dxl_present_velocity[3]*DXL_VELOCITY_RESOLUTION * RPM2Rad]

        self.joint_states.position = q_current
        self.joint_states.velocity = qdot_current
        
        ### TO DO : Uncomment below ###
        self.joint_states_pub.publish(self.joint_states)
        #self.joint_states_pub_tmp.publish(self.joint_states)

    def write_dxl(self):
        ### TO DO : Uncomment 3 and 4 ###
        dxl_addparam_result = self.groupSyncWrite.addParam(DXL1_ID, self.dxl_goal_position[0])
        dxl_addparam_result = self.groupSyncWrite.addParam(DXL2_ID, self.dxl_goal_position[1])
        dxl_addparam_result = self.groupSyncWrite.addParam(DXL3_ID, self.dxl_goal_position[2])
        dxl_addparam_result = self.groupSyncWrite.addParam(DXL4_ID, self.dxl_goal_position[3])

        dxl_comm_result = self.groupSyncWrite.txPacket()
        self.groupSyncWrite.clearParam()
        

    def error_check(self,dxl_comm_result, dxl_error):
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))


def main():
    rospy.init_node('DXL_pos_control')

    try:
        dxl_pos = DynamixelPositionControl()
    except rospy.ROSInterruptException:
        pass

    rospy.spin()

if __name__ == '__main__':
    main()
