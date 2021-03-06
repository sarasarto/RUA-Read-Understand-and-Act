# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from . import project_parameters as params

class MapConstructor():

    def __init__(self):
        pass

    def circle_around_signal(self, planimetry, xc , yc, radius):
        for r in range(planimetry.shape[0]):
            for c in range(planimetry.shape[1]):
                if (r-xc)**2 + (c - yc)**2 <= radius ** 2:
                    planimetry[r,c] = 0

        return planimetry

    def construct_planimetry(self, matrix_3d_points, signal_3d_point = None, signal = False):
        y_left = np.max(matrix_3d_points[:,:,1]) #max because y is positive to left
        y_right = np.min(matrix_3d_points[:,:,1])
        y_range = np.abs(y_left - y_right)
        middle_position = int(np.round(y_range / 2))
        MAX_DEPTH_EXPLORATION = 150

        if signal:
            signal_depth = signal_3d_point[0]
            max_depth = signal_depth
        else:
            max_depth = MAX_DEPTH_EXPLORATION  # da mettere tra parametri

        coordinates_X = matrix_3d_points[:,:,0]
        coordinates_Z = matrix_3d_points[:,:,2]

        mask = np.logical_and(coordinates_Z > (params.FLOOR_HEIGHT_LIMIT * 100), coordinates_Z < (params.ROBOT_HEIGHT * 100))
        mask = np.logical_and(mask, coordinates_X < max_depth)

        obstacles = matrix_3d_points[mask==True]
        x_coords = obstacles[:,0]
        y_coords = middle_position - obstacles[:,1]
        
        planimetry = np.zeros((max_depth, y_range))
        planimetry[x_coords, y_coords - 1] = 255
        planimetry = np.where(planimetry < 0, 0, planimetry) #We put 0 for values which can become negative

        robot_coords = [0, middle_position]
        
        if signal:
            signal_coords = [signal_depth, middle_position - signal_3d_point[1]]
            planimetry, robot_coords, signal_coords = self._clip_planimetry(planimetry, robot_coords, signal_coords)
            return planimetry, robot_coords, signal_coords
        else:
            return planimetry, robot_coords, None
            
    def _clip_planimetry(self, planimetry, robot_coords, signal_coords):
        old_y_difference=  robot_coords[1] - signal_coords[1]
        boundary_left = np.max(planimetry, axis=0) 
        boundary_left = np.argmax(boundary_left) 
        
        flipped_matrix = planimetry[:,::-1]
        boundary_right = np.max(flipped_matrix, axis=0)
        boundary_right = np.argmax(boundary_right) 
        boundary_right = planimetry.shape[1] - boundary_right 
        

        if robot_coords[1] < boundary_left:
            boundary_left = robot_coords[1]
            robot_coords = (0, 0)
        elif robot_coords[1] > boundary_right:
            boundary_right = robot_coords[1]
            y_robot = robot_coords[1] - boundary_left - 1 #-1 in order to include robot limit
            robot_coords = (0, y_robot)
        else:
            # BL    R ___X CM ___BR
            planimetry_dim  = boundary_right - boundary_left
            robot_distance_from_right = robot_coords[1] - boundary_right
            robot_coords = self._recompute_robot_coords(robot_distance_from_right, planimetry_dim)      
        
        
        planimetry = planimetry[:, boundary_left:boundary_right]
        new_signal_coords = self._recompute_signal_coords(robot_coords,old_y_difference, signal_coords)
        return planimetry, robot_coords, new_signal_coords 

    def _recompute_signal_coords(self,robot_coords, old_y_difference, signal_coords):
        # .R    .S          # .S   .R
        # R-S <0                R-S >0
        # NEW_SEGNALE = R_NEW - DIFFERENCE 
        y_signal = robot_coords[1] - old_y_difference 
        return (signal_coords[0], y_signal)

    def _recompute_robot_coords(self, robot_bound_distance, planimetry_dim):
        # BL    R ___10CM ___BR
        y_robot = planimetry_dim + robot_bound_distance 
        return (0, y_robot)
