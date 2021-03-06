# -*- coding: utf-8 -*-
from matplotlib.pyplot import axes
import numpy as np
from .node import Node
import time
import copy

class PathPlanner():
    def return_path(self, current_node):
        path = []
        current = current_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1]  # Return reversed path

    def shrink_path(self, paths):
        THRESHOLD = 25

        point = paths[0]
        shrink_paths = []

        for i in range(1, len(paths)):
            if ( abs(point[0] - paths[i][0]) > THRESHOLD )  and ( abs(point[1]) - paths[i][1] ):
                shrink_paths.append(paths[i])
                point = paths[i]
        
        shrink_paths.append(paths[-1])

        return shrink_paths
        
    
    def clean_shrink_path(self, path, signal_coords):
        last_point = path[-1]
        last_distance = np.sqrt( (last_point[0] - signal_coords[0]) ** 2 + (last_point[1] - signal_coords[1]) ** 2)

        penultimate_point = path[-2]
        penultimate_distance = np.sqrt( (penultimate_point[0] - signal_coords[0]) ** 2 + (penultimate_point[1] - signal_coords[1]) ** 2)

        if penultimate_distance < last_distance:
            path = path[: -1]
        return path


    def compute(self, maze, start, end, allow_diagonal_movement = False):
        """
        Returns a list of tuples as a path from the given start to the given end in the given maze
        :param maze:
        :param start:
        :param end:
        :param allow_diagonal_movement: do we allow diagonal steps in our path
        :return:
        """
        start_time = time.time()
        # Create start and end node
        start_node = Node(None, start)
        start_node.g = start_node.h = start_node.f = 0
        end_node = Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start node
        open_list.append(start_node)
        
        # Adding a stop condition
        outer_iterations = 0
        max_iterations = (len(maze) // 2) ** 2
        #max_iterations = 10000

        # what squares do we search
        adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0),)
        if allow_diagonal_movement:
            adjacent_squares = ((0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1),)

        # Loop until you find the end or when time is over
        
        while len(open_list) > 0  :
            if (time.time() - start_time) > 0.5:
                return self.return_path(current_node)
            
            outer_iterations += 1
            
            # Get the current node
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index
                    
            if outer_iterations > max_iterations:
                # if we hit this point return the path such as it is
                # it will not contain the destination
                print("giving up on pathfinding too many iterations")
                return self.return_path(current_node)

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)
            x = current_node.position[0]
            y = current_node.position[1]
            if np.sqrt(np.power((x-end[0]), 2) + np.power((y-end[1]),2) ) < 7:
                return self.return_path(current_node)

            # Found the goal
            if current_node == end_node:
                print('Algorithm found a path to destination!')
                return self.return_path(current_node)

            # Generate children
            children = []
            
            for new_position in adjacent_squares:  # Adjacent squares

                # Get node position
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                # Make sure within range
                within_range_criteria = [
                    node_position[0] > (len(maze) - 1),
                    node_position[0] < 0,
                    node_position[1] > (len(maze[len(maze) - 1]) - 1),
                    node_position[1] < 0,
                ]
                
                if any(within_range_criteria):
                    continue

                # Make sure walkable terrain
                if maze[node_position[0]][node_position[1]] != 0:
                    continue

                # Create new node
                new_node = Node(current_node, node_position)

                # Append
                children.append(new_node)

            # Loop through children
            for child in children:
                
                # Child is on the closed list
                if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                    continue

                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0]) ** 2) + \
                        ((child.position[1] - end_node.position[1]) ** 2)
                child.f = child.g + child.h

                # Child is already in the open list
                if len([open_node for open_node in open_list if child == open_node and child.g > open_node.g]) > 0:
                    continue

                # Add the child to the open list
                open_list.append(child)

                #I just want to do steps of 1m, so i stop when i get to 150
                if child.position[0] > 150:
                    return self.return_path(current_node)
