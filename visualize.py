import pygame as pg
import random as rd
import time

from world import World

cell_size = 50
border_size = 2


class Visualize:
    def __init__(self, world):
        self.world = world
        self.window = None
        self.num_row = self.world.num_row
        self.num_col = self.world.num_column
        self.colors = Visualize.color_gradient(self.world.num_agent)

    def init(self):
        window_width = self.num_col * cell_size
        window_height = self.num_row * cell_size
        pg.init()
        self.window = pg.display.set_mode((window_width, window_height))
        pg.display.set_caption("AutoStore")

    def update(self) -> bool:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close()
                return False

        for row in range(self.num_row):
            for col in range(self.num_col):
                color = (255, 255, 255)
                x = col * cell_size
                y = row * cell_size
                pg.draw.rect(self.window, color, (x, y, cell_size, cell_size))

        for i in range(len(self.world.agents)):
            x, y = self.world.agents[i].current
            x *= cell_size
            y *= cell_size
            pg.draw.rect(self.window, self.colors[i], (x, y, cell_size, cell_size))

        for i in range(len(self.world.agents)):
            goal_x, goal_y = self.world.agents[i].goal
            goal_x *= cell_size
            goal_y *= cell_size
            pg.draw.circle(self.window, self.colors[i], (goal_x + cell_size / 2, goal_y + cell_size / 2), cell_size / 3)

        for row in range(self.num_row):
            for col in range(self.num_col):
                x = col * cell_size
                y = row * cell_size
                pg.draw.rect(self.window, (0, 0, 0), (x, y, cell_size, cell_size), border_size)

        pg.display.flip()
        return True

    @staticmethod
    def color_gradient(num_agent):
        res = []
        for x in [0, 127, 255]:
            for y in [0, 127, 255]:
                for z in [0, 127, 255]:
                    if x == 0 and y == 0 and z == 0:
                        continue
                    if x == 255 and y == 255 and z == 255:
                        continue
                    res.append((x, y, z))
        res.sort(key=lambda _x: rd.randint(0, 10))
        # just prevent num_agent > 25
        for x in [0, 127, 255]:
            for y in [0, 127, 255]:
                for z in [0, 127, 255]:
                    if x == 0 and y == 0 and z == 0:
                        continue
                    if x == 255 and y == 255 and z == 255:
                        continue
                    res.append((x, y, z))
        return res

    @staticmethod
    def close():
        pg.quit()


my_world = World()
visualize = Visualize(my_world)

visualize.init()

isRunning = True

isComplete = False

while isRunning:
    for agent in my_world.agents:
        agent.update()
    isRunning = visualize.update()
    time.sleep(0.1)
