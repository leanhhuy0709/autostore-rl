import pygame as pg
import random as rd
import time
from config import Args
from agent import *
import matplotlib.pyplot as plt

from world import World

cell_size = Args.cell_size
border_size = Args.border_size


class Visualize:
    def __init__(self, world):
        self.world = world
        self.window = None
        self.font = None
        self.num_row = self.world.num_row
        self.num_col = self.world.num_column
        self.colors = Visualize.color_gradient(self.world.num_agent)

    def init(self):
        window_width = self.num_col * cell_size + 400
        window_height = self.num_row * cell_size
        pg.init()
        self.window = pg.display.set_mode((window_width, window_height))
        pg.display.set_caption("AutoStore")

        pg.font.init()
        self.font = pg.font.SysFont('Comic Sans MS', int(cell_size/2))

    @property
    def update(self) -> bool:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close()
                return False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    return False

        self.window.fill((255, 255, 255))

        for j in range(len(self.world.agents)):
            x = self.num_col * cell_size + 50
            y = j * cell_size
            pg.draw.rect(self.window, self.colors[j], (x, y, cell_size, cell_size))

        for j in range(len(self.world.agents)):
            x = self.num_col * cell_size + 50
            y = j * cell_size
            pg.draw.rect(self.window, (0, 0, 0), (x, y, cell_size, cell_size), border_size)

        for j in range(len(self.world.agents)):
            x = self.num_col * cell_size + 125
            y = j * cell_size + cell_size/8
            text_surface = self.font.render(str(len(DataPlot.real_lengths[j])), False, (0, 0, 0))
            self.window.blit(text_surface, (x, y))

        for j in range(len(self.world.agents)):
            x = self.num_col * cell_size + 200
            y = j * cell_size + cell_size/8
            value = round(self.world.agents[j].count, 1) # round(DataPlot.time[j], 1)
            if value <= 0:
                value = 0
            text_surface = self.font.render(str(value), False, (0, 0, 0))
            self.window.blit(text_surface, (x, y))

        for j in range(len(self.world.agents)):
            x = self.num_col * cell_size + 300
            y = j * cell_size + cell_size/8
            text_surface = self.font.render(str(DataPlot.ideal_lengths[j][len(DataPlot.ideal_lengths[j]) - 1]),
                                            False, (0, 0, 0))
            self.window.blit(text_surface, (x, y))

        for row in range(self.num_row):
            for col in range(self.num_col):
                color = (255, 255, 255)
                x = col * cell_size
                y = row * cell_size
                pg.draw.rect(self.window, color, (x, y, cell_size, cell_size))

        for j in range(len(self.world.agents)):
            x, y = self.world.agents[j].current
            x *= cell_size
            y *= cell_size
            pg.draw.rect(self.window, self.colors[j], (x, y, cell_size, cell_size))

        for j in range(len(self.world.agents)):
            goal_x, goal_y = self.world.agents[j].goal
            goal_x *= cell_size
            goal_y *= cell_size
            pg.draw.circle(self.window, self.colors[j], (goal_x + cell_size / 2, goal_y + cell_size / 2), cell_size / 3)

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


class DataPlot:
    ideal_lengths = []
    real_lengths = []
    time = []
    count = []


my_world = World()
visualize = Visualize(my_world)

visualize.init()

for i in range(len(my_world.agents)):
    agent = my_world.agents[i]
    agent.set_speed(0.1)
    DataPlot.ideal_lengths.append([])
    DataPlot.real_lengths.append([])
    DataPlot.time.append(0)
    DataPlot.count.append(0)

    d = abs(agent.goal[1] - agent.next[1]) + abs(agent.goal[0] - agent.next[0])
    DataPlot.ideal_lengths[i].append(d)
    agent.epsilon = 0.1

isRunning = True
isComplete = False
delay = 0.1
step = 0.1
Time = 0

num_complete = 0

while isRunning:
    for i in range(len(my_world.agents)):
        agent = my_world.agents[i]
        agent.handle_move()

        DataPlot.time[i] += 0.1

        if agent.next == agent.goal and agent.move_state == MoveState.IDLE:
            num_complete += 1
            print("Complete: " + str(num_complete))

            new_goal = my_world.generate_random_position_with_distance(agent.prev, 1)
            DataPlot.real_lengths[i].append(round(agent.count, 1))
            agent.reset(new_goal)
            DataPlot.ideal_lengths[i].append(abs(agent.goal[1] - agent.next[1]) + abs(agent.goal[0] - agent.next[0]))

    isRunning = visualize.update
    Time += 0.1
    time.sleep(0.05)

# Draw Plot
for i in range(len(my_world.agents)):
    DataPlot.ideal_lengths[i].pop()


def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list


DataPlot.ideal_lengths = flatten_list(DataPlot.ideal_lengths)
DataPlot.real_lengths = flatten_list(DataPlot.real_lengths)

DataPlot.real_lengths = list(map(lambda x: round(x), DataPlot.real_lengths))
print(DataPlot.ideal_lengths)
print(DataPlot.real_lengths)

val = []
temp = []
val2 = []

for i in range(len(DataPlot.ideal_lengths)):
    if DataPlot.ideal_lengths[i] == 0:
        DataPlot.ideal_lengths[i] = 1
    val.append(DataPlot.real_lengths[i] / DataPlot.ideal_lengths[i])

for i in range(len(DataPlot.ideal_lengths)):
    val2.append(DataPlot.real_lengths[i] - DataPlot.ideal_lengths[i])

sum_val = 0
sum_val2 = 0
y3 = []
y4 = []
for i in range(len(val)):
    sum_val += val[i]
    sum_val += val2[i]
    y3.append(sum_val / (i + 1))
    y4.append(sum_val / (i + 1))
    # y3.append(val2[i])

plt.plot(range(len(val)), y3, marker='o', linestyle='-', color='red', label='Rate')
plt.plot(range(len(val)), y4, marker='o', linestyle='-', color='blue', label='Rate')

plt.xlabel('ith completions')
plt.ylabel('Average ratio between real path and ideal path')

plt.title('Ratio graph between actual and ideal path with 20000 trains')

plt.legend()

plt.show()
