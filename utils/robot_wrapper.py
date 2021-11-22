# -*- coding: utf-8 -*-
import numpy as np
from .geometry_transformation import GeometryTransformation

class RobotWrapper():
    def __init__(self, lab_mode="True"):
        self.lab_mode = lab_mode
        self.robot = None

        if self.lab_mode == "True":
            from pyrobot import Robot
            self.robot = Robot('locobot')
            self.camera = self.robot.camera
       
    def get_rgbd_frame(self):
        rgb_img, depth_img = self.camera.get_rgb_depth()
        return rgb_img, depth_img

    def get_intrinsic_matrix(self):
        return self.camera.get_intrinsics()

    def reach_relative_point(self, x, y, theta=0.0):
        target_position = [x, y, theta]
        self.robot.base.go_to_relative(target_position, smooth=False, close_loop=True)

    def reach_absolute_point(self, x, y, theta=0.0):
        target_position = [x, y, theta]
        self.robot.base.go_to_absolute(target_position, smooth=False, close_loop=True)

    def turn(self, angle_radiant):
        target_position = [0.0, 0.0, angle_radiant]
        self.robot.base.go_to_relative(target_position, smooth=False, close_loop=True)

    def _reset_robot_global_position(self):
        self.robot.base.base_state.state.update((0,0,0))

    def follow_trajectory(self, trajectory, robot_coords):    
        pose_x, pose_y, pose_yaw = self.robot.base.get_state('odom')
        print('Pos coords: {}, {}'.format(pose_x, pose_y))
        starting_pose = np.array([pose_x, pose_y, pose_yaw])
        y_robot = robot_coords[1]

        old_path = (0,0)

        for i in range(len(trajectory)):
            if old_path == (0,0):
                y_new = trajectory[i][1] / 100.0
            else:
                y_new = (y_robot - trajectory[i][1])/100.0

            print('Considered coords: {}'.format(trajectory[i]))
            print('Old path: {}'.format(old_path))
            print('Starting pose: {}'.format(starting_pose))

            x_new = trajectory[i][0]/100.0
            x_new -= (old_path[0] / 100.0)
            y_new -= ((y_robot - old_path[1]) / 100.0)

            print(x_new, y_new)
            current_pose = starting_pose + np.array([x_new,y_new,0.0])
            print('Current pose: {}'.format(current_pose))

            gt = GeometryTransformation()
            coords = gt.coordinate_projection(starting_pose, current_pose)
           
            print('Final coordinates: {}'.format(coords))
        
            starting_pose = current_pose     
            old_path = trajectory[i]
            
            if abs(coords[0][1]) < 0.1:
                coords[0][1] = 0.0
        
            self.reach_relative_point(coords[0][0], coords[0][1])


    def follow_trajectory_with_update(self, trajectory, old_robot_coords):
        """
        This function assumes that input trajectory contains points which coordinates 
        refer to a global planimetry
        """
        #convert list of tuples to numpy array
        trajectory = np.array(trajectory)
        self._reset_robot_global_position() #reset global robot position to (0,0)

        #update y_coordinates to fit with the new reference system
        trajectory[1] -= old_robot_coords[1]

        #now we have the new x and y coordinates. we can follow the trajectory
        #we compute theta angle in order to avoid robot repositioning each time
        for i in range(len(trajectory)):
            x = trajectory[i,0]
            y = trajectory[i,1]
            theta = np.atan2(y,x)
            self.reach_absolute_point(x, 0.0, theta) #passing theta instead of x,y should avoid robot repositioning!