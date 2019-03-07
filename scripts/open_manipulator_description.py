#-----------------------------------------------------------------------
# Tasks:
# 1. Returns M0 matrix and body twists for Sawyer
#
# Obtained from Chainatee Tanakulrungson
#-----------------------------------------------------------------------

import numpy as np
# DH matrix
# Blist: The joint screw axes in the end-effector frame when the 
# manipulator is at the home position,


Blist = np.array([[-1., 0., 0., 0., 0.186, 0.],
                  [0., 1.0, 0., 0.1281, 0., -0.278],
                  [0., 1.0, 0., 0., 0., -0.254],
                  [0., 1.0, 0.0, 0., 0., -0.13]])
Blist = Blist.T

# Homogen TF matrix from base to robot's end-effector

# M: The home configuration (position and orientation) of the 
#         end-effector
# Should make it automated
# use tf.transformation to change from ee_pose + quaternion to homogen tf 


M = np.array([[1.0, 0., 0., 0.29],
              [0, 1.0, 0., 0.0],
              [0., 0.0, 1., 0.20305],
              [0., 0., 0., 1.]])


# # Mlist: List of link frames i relative to i-1 at the home position
# M01 = np.array([[1, 0, 0,        0],
#                 [0, 1, 0,        0],
#                 [0, 0, 1, 0.089159],
#                 [0, 0, 0,        1]])
# M12 = np.array([[0, 0, 1,    0.28],
#                 [0, 1, 0, 0.13585],
#                 [-1, 0, 0,       0],
#                 [0, 0, 0,       1]])
# M23 = np.array([[1, 0, 0,       0],
#                 [0, 1, 0, -0.1197],
#                 [0, 0, 1,   0.395],
#                 [0, 0, 0,       1]])
# M34 = np.array([[1, 0, 0,       0],
#                 [0, 1, 0,       0],
#                 [0, 0, 1, 0.14225],
#                 [0, 0, 0,       1]])
# M45 = np.array([[1, 0, 0,       0],
#                 [0, 1, 0,       0],
#                 [0, 0, 1, 0.14225],
#                 [0, 0, 0,       1]])
# M56 = np.array([[1, 0, 0,       0],
#                 [0, 1, 0,       0],
#                 [0, 0, 1, 0.14225],
#                 [0, 0, 0,       1]])
# M67 = np.array([[1, 0, 0,       0],
#                 [0, 1, 0,       0],
#                 [0, 0, 1, 0.14225],
#                 [0, 0, 0,       1]])                        
# Mlist = np.array([M01, M12, M23, M34, M45, M56, M67])

# # Glist: Spatial inertia matrices Gi of the links
# G1 = np.diag([0.010267, 0.010267, 0.00666, 3.7, 3.7, 3.7])
# G2 = np.diag([0.22689, 0.22689, 0.0151074, 8.393, 8.393, 8.393])
# G3 = np.diag([0.0494433, 0.0494433, 0.004095, 2.275, 2.275, 2.275])
# G4 = np.diag([0.010267, 0.010267, 0.00666, 3.7, 3.7, 3.7])
# G5 = np.diag([0.22689, 0.22689, 0.0151074, 8.393, 8.393, 8.393])
# G6 = np.diag([0.0494433, 0.0494433, 0.004095, 2.275, 2.275, 2.275])
# G7 = np.diag([0.010267, 0.010267, 0.00666, 3.7, 3.7, 3.7])
# Glist = np.array([G1, G2, G3, G4, G5, G6, G7])              

# Slist :  The joint screw axes in the space frame when the manipulator is at the home position
Slist = np.array([[ -1.0,       0.,       0.,      0.,  -0.01705,       0. ],
                [ 0.,       1.,       0.,      -0.07495,  0.,       0.012  ],
                [ 0.,       1.,       0.,      -0.20305,  0.,       0.036  ],
                [ 0.,       1.,       0.,      -0.20305,  0.,       0.16   ]])
Slist = Slist.T