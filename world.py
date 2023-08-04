from config import *
from agent import Agent
import random as rd
from wall import Wall


class World:
    def __init__(self):
        self.num_row = Args.num_row
        self.num_column = Args.num_column
        self.num_agent = Args.num_agent

        self.prev_matrix = {}
        self.next_matrix = {}

        self.agents = []

        self.num_wall = len(Args.CUSTOM_WALL)
        self.walls = []
        self.wall_matrix = {}

        for i in range(self.num_wall):
            wall_position = Args.CUSTOM_WALL[i]
            x, y = wall_position
            if x < 0 or x >= self.num_row or y < 0 or y >= self.num_column:
                continue

            curr_wall = Wall(wall_position)
            curr_wall.set_world(self)
            self.prev_matrix[wall_position] = curr_wall
            self.next_matrix[wall_position] = curr_wall
            self.wall_matrix[wall_position] = curr_wall
            self.walls.append(curr_wall)

        for i in range(self.num_agent):
            start_position = self.generate_random_empty_position()
            goal_position = self.generate_random_position()

            agent = Agent(start_position, goal_position)
            agent.set_world(self)
            self.agents.append(agent)
            self.prev_matrix[start_position] = agent
            self.next_matrix[start_position] = agent

    def generate_random_empty_position(self):
        for i in range(100):
            x = rd.randint(0, self.num_column - 1)
            y = rd.randint(0, self.num_row - 1)

            if (x, y) in self.prev_matrix or (x, y) in self.next_matrix or (x, y) in self.wall_matrix:
                pass
            else:
                return x, y
        print("Error, can't generate empty position")
        return -1, -1

    def generate_random_position_with_distance(self, start_position, d: int):
        xSt, ySt = start_position
        for i in range(100):
            x = rd.randint(0, self.num_column - 1)
            y = rd.randint(0, self.num_row - 1)

            if (x - xSt) ** 2 + (y - ySt) ** 2 < d * d or (x, y) in self.wall_matrix:
                pass
            else:
                return x, y
        print("Error, can't generate random position with distance")
        return self.generate_random_position()

    def generate_random_position(self):
        for i in range(100):
            x = rd.randint(0, self.num_column - 1)
            y = rd.randint(0, self.num_row - 1)

            if (x, y) in self.wall_matrix:
                pass
            else:
                return x, y
        print("Error, can't generate empty position")
        return -1, -1

    def remove_prev_matrix(self, position: tuple[int, int]):
        self.prev_matrix.pop(position)

    def remove_next_matrix(self, position: tuple[int, int]):
        self.next_matrix.pop(position)

    def add_prev_matrix(self, position: tuple[int, int], agent: Agent):
        self.prev_matrix[position] = agent

    def add_next_matrix(self, position: tuple[int, int], agent: Agent):
        self.next_matrix[position] = agent
