from config import *
from agent import Agent
import random as rd


class World:
    def __init__(self):
        self.num_row = Args.num_row
        self.num_column = Args.num_column
        self.num_agent = Args.num_agent

        self.prev_matrix = {}
        self.next_matrix = {}

        self.agents = []

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

            if (x, y) in self.prev_matrix or (x, y) in self.next_matrix:
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

            if (x - xSt) ** 2 + (y - ySt) ** 2 < d * d:
                pass
            else:
                return x, y
        print("Error, can't generate random position with distance")
        return self.generate_random_position()

    def generate_random_position(self):
        x = rd.randint(0, self.num_column - 1)
        y = rd.randint(0, self.num_row - 1)
        return x, y

    def remove_prev_matrix(self, position: tuple[int, int]):
        self.prev_matrix.pop(position)

    def remove_next_matrix(self, position: tuple[int, int]):
        self.next_matrix.pop(position)

    def add_prev_matrix(self, position: tuple[int, int], agent: Agent):
        self.prev_matrix[position] = agent

    def add_next_matrix(self, position: tuple[int, int], agent: Agent):
        self.next_matrix[position] = agent
