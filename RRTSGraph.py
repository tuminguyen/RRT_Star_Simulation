import pygame
import random
import numpy as np
import math
import os
import sys

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(THIS_DIR))
print(os.path.dirname(THIS_DIR))
from utils import triangle_collide


class RRTSGraph:
    def __init__(self, start, target, obstacles, tri_checklist, rect_checklist, step_size):
        self.start = start
        self.target = target
        self.start_rec = pygame.Rect(self.start[0] - 15, self.start[1] - 15, 30, 30)
        self.target_rec = pygame.Rect(self.target[0] - 15, self.target[1] - 15, 30, 30)
        self.obstacles = obstacles
        self.tri_checklist = tri_checklist
        self.rect_checklist = rect_checklist
        self.step_size = step_size
        self.map_w = 1200
        self.map_h = 800
        # init
        self.xs = list()
        self.xs.append(self.start[0])
        self.ys = list()
        self.ys.append(self.start[1])
        self.parents = list()
        self.parents.append(0)
        self.costs = list()
        self.costs.append(0)
        # goal status
        self.stoppable_dist = 25
        self.finish_flag = False
        self.finish_index = None
        # path - a list includes nodes/steps
        self.path = list()
        # graph config
        self.space_dim = 2
        self.planning_const = 200

    def n_nodes(self):
        """
        return the number of nodes in graph
        :return:
        """
        return len(self.xs)

    def random_node(self):
        x = int(random.uniform(0, self.map_w - 4))
        y = int(random.uniform(0, self.map_h - 4))
        return x, y

    def add_node(self, idx, x, y):
        """
        add new node to graph with index (insert an element to x and y list)
        :param idx: index of the node
        :param x: x-coordinate
        :param y: y-coordinate
        :return:
        """
        self.xs.insert(idx, x)
        self.ys.insert(idx, y)

    def remove_node(self, idx):
        """
        remove node from graph by corresponding index (pop out an element from x and y list)
        :param idx: index of the node
        :return:
        """
        self.xs.pop(idx)
        self.ys.pop(idx)

    def get_cost(self, idx):
        """
        Return cost from the node index to start node.
        :param idx: node index
        :return:
        """
        par_idx = self.parents[idx]
        return self.costs[par_idx] + self.distance(idx, par_idx)

    def add_edge(self, child, parent):
        """
        create relationship between 2 nodes
        :param child: index of the child node
        :param parent: index of the parent node
        :return:
        """
        self.parents.insert(child, parent)
        # self.costs.insert(child, self.distance(child, parent))
        self.costs.insert(child, self.get_cost(parent) + self.distance(child, parent))

    def remove_edge(self, idx):
        """
        delete the relationship between the parent and the child node
        :param idx: child node's index
        :return:
        """
        self.parents.pop(idx)

    def is_collided(self, x, y):
        """
        Checking collision between new node and obstacles/lines/start/target
        :param x: node's x
        :param y: node's y
        :return:
        """
        if self.start_rec.collidepoint(x, y) or self.target_rec.collidepoint(x, y):
            return True
        else:
            for obs in self.obstacles:
                if obs.collidepoint(x, y):
                    return True
            for tri in self.tri_checklist:
                if triangle_collide((x, y), tri[0], tri[1], tri[2]):
                    return True
            for rect in self.rect_checklist:
                if pygame.Rect(rect).collidepoint(x, y):
                    return True
            return False

    def avoid_things(self, idx1, idx2):
        """
        check if the edge between 2 nodes cross/collide anything
        :param idx1: index of node 1
        :param idx2: index of node 2
        :return:
        """
        x1, y1 = self.xs[idx1], self.ys[idx1]
        x2, y2 = self.xs[idx2], self.ys[idx2]
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        if width == 0:
            width = 1
        if height == 0:
            height = 1
        rect_line = pygame.Rect((min(x1, x2), min(y1, y2)), (width, height))
        for obs in self.obstacles:
            if obs.colliderect(rect_line):
                return True
        for r in self.rect_checklist:
            if pygame.Rect(r).colliderect(rect_line):
                return True
        for t in self.tri_checklist:
            if triangle_collide((x1, y1), t[0], t[1], t[2]) or \
                    triangle_collide((x2, y2), t[0], t[1], t[2]) or \
                    triangle_collide((min(x1, x2), min(y1, y2)), t[0], t[1], t[2]) or \
                    triangle_collide((max(x1, x2), max(y1, y2)), t[0], t[1], t[2]):
                return True
        return False

    def distance(self, idx1, idx2):
        """
        calculate the distance between 2 nodes
        :param idx1: index of node 1
        :param idx2: index of node 2
        :return:
        """
        # current using euclidean
        node_1 = np.array((self.xs[idx1], self.ys[idx1]))
        node_2 = np.array((self.xs[idx2], self.ys[idx2]))
        return int(np.linalg.norm(node_1 - node_2))

    def init_nearest(self, idx):
        """
        Find the nearest node from the given node with corresponding index
        :param idx: node's index
        :return: index of the nearest node
        """
        # calculate distance from root (start node)
        d_near = self.distance(0, idx)
        # index of the nearest node
        idx_near = 0
        # update loop
        for i in range(0, idx):
            dist = self.distance(i, idx)
            if dist < d_near:
                d_near = dist
                idx_near = i
        return idx_near

    def neighbours_in_range(self, x, y, radius):
        """
        Find node in range of radius
        :param x: node's x
        :param y: node's y
        :param radius: radius of searching circle
        :return:
        """
        neighbours = list()
        for idx in range(len(self.xs)):
            if x - radius <= self.xs[idx] <= x + radius and y - radius <= self.ys[idx] <= y + radius:
                neighbours.append(idx)
        return neighbours

    def step(self, idx_near, idx_rand, max_dist=18):
        """
        Find the real new node B on the line created from A (idx_near) and C (idx_rand).
        B should be as near as possible to C, but the distance from B->A can not exceed a threshold (max_dist).
        #####################################################
        -|               C
        -|              /
        -|             /
        -|            /
        -|           /B     # n = divided step length
        -|          / |     # theta not in degree, in Pi
        -|       n /  |     # xB = xA + n * cos(theta)
        -|        /   |     # yB = yA + n * sin(theta)
        -|       A----|
        -|----------------------------> x
        #####################################################
        :param idx_near: index of the nearest node (must be 1 of the existed nodes on the graph) to the random one
        :param idx_rand: index of the random node
        :param max_dist: the max distance that B can be far from A
        :return:
        """
        dist = self.distance(idx_near, idx_rand)
        if dist > max_dist:
            # get coordinates for A
            x_near, y_near = self.xs[idx_near], self.ys[idx_near]
            # get coordinates for C
            x_rand, y_rand = self.xs[idx_rand], self.ys[idx_rand]
            # calculate angle step length and find new B
            delta = (abs(x_rand - x_near), abs(y_rand - y_near))
            theta = math.atan2(delta[1], delta[0])
            if x_rand > x_near:
                x = int(x_near + max_dist * math.cos(theta))
            elif x_rand < x_near:
                x = int(x_near - max_dist * math.cos(theta))
            else:
                x = x_near
            if y_rand > y_near:
                y = int(y_near + max_dist * math.sin(theta))
            elif y_rand < y_near:
                y = int(y_near - max_dist * math.sin(theta))
            else:
                y = y_near
            self.remove_node(idx_rand)
            self.add_node(idx_rand, x, y)
            if abs(x - self.target[0]) <= self.stoppable_dist and abs(y - self.target[1]) <= self.stoppable_dist:
                print("GOAL!!!!")
                self.add_edge(idx_rand, idx_near)
                self.finish_index = idx_rand
                self.finish_flag = True
            else:
                if self.is_collided(x, y) is False:
                    r = self.planning_const * (math.log(self.n_nodes(), 10) / (self.n_nodes())) ** (1 / self.space_dim)
                    neighbours = self.neighbours_in_range(x, y, r)
                    neighbours.remove(idx_rand)
                    if len(neighbours) == 1:

                        if self.avoid_things(idx_near, idx_rand) is False:
                            self.add_edge(idx_rand, idx_near)
                        else:
                            self.remove_node(idx_rand)
                    else:
                        if self.choose_parent(idx_rand, neighbours):
                            self.rewire(idx_rand, neighbours)
                        else:
                            if self.avoid_things(idx_near, idx_rand) is False:
                                self.add_edge(idx_rand, idx_near)
                            else:
                                self.remove_node(idx_rand)
                else:
                    self.remove_node(idx_rand)
        else:
            self.remove_node(idx_rand)

    def choose_parent(self, idx_rand, neighbours):
        """
        Find the node which is best as parent
        :param idx_rand: random node
        :param neighbours: list of neighbours in specific radius
        :return:
        """
        dlist = [self.get_cost(neigh) + self.distance(neigh, idx_rand) for neigh in neighbours]
        sorted_idx = [idx for _, idx in sorted(zip(dlist, neighbours))]

        for idx in sorted_idx:
            if self.avoid_things(idx, idx_rand) is False:
                self.add_edge(idx_rand, idx)
                return True
        return False

    def rewire(self, idx_rand, neighbours):
        """
        rewire the nodes of graph
        :param idx_rand:
        :param idx_near:
        :param neighbours:
        :return:
        """
        cost_x_rand = self.get_cost(idx_rand)
        for neigh_idx in neighbours:
            if cost_x_rand + self.distance(idx_rand, neigh_idx) < self.get_cost(neigh_idx):
                if self.avoid_things(neigh_idx, idx_rand) is False:
                    self.parents[neigh_idx] = idx_rand
                    self.costs[neigh_idx] = cost_x_rand + self.distance(idx_rand, neigh_idx)

    def bias(self, target):
        """
        Generate new node from Target
        :param target:
        :return:
        """
        last_idx = self.n_nodes()
        # add the target as the last node in the graph
        self.add_node(last_idx, target[0], target[1])
        # get nearest node in graph to the target
        idx_near = self.init_nearest(last_idx)
        # create a connection
        self.step(idx_near, last_idx)
        return self.xs, self.ys, self.parents

    def extend(self):
        """
        Extend the graph
        :return:
        """
        last_idx = self.n_nodes()
        x, y = self.random_node()
        if self.is_collided(x, y) is False:
            self.add_node(last_idx, x, y)
            idx_near = self.init_nearest(last_idx)
            self.step(idx_near, last_idx)
        return self.xs, self.ys, self.parents

    def path_history(self):
        if self.finish_flag:
            self.path = []
            self.path.append(self.finish_index)
            pos = self.parents[self.finish_index]
            while pos != 0:
                self.path.append(pos)
                pos = self.parents[pos]
            self.path.append(0)
        return self.path

    def get_path_nodes(self):
        coordinates = list()
        for node in self.path:
            x, y = self.xs[node], self.ys[node]
            coordinates.append((x, y))
        return coordinates
