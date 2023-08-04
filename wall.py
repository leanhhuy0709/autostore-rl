"""
Wall is 1 Agent but not moving
"""
from agent import Agent


class Wall(Agent):
    def __init__(self, position: tuple[int, int]):
        super().__init__(position, position)
        self.position = position

    def set_world(self, world):
        self.world = world
