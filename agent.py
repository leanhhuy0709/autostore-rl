import random
from typing import Any
from tensorflow.keras.models import save_model, load_model
from config import Args, Action
import random as rd
import numpy as np

STEP = 0.2

loaded_model = load_model(Args.model_filename)


class MoveState:
    MOVING = 0
    IDLE = 1


class Agent:
    def __init__(self, start_position: tuple[int, int], goal_position: tuple[int, int]):
        self.world = None
        self.prev = None
        self.current = None
        self.next = None
        self.is_alive = None
        self.move_state = MoveState.IDLE

        self.gamma = None
        self.epsilon_decrement = None
        self.goal = None
        self.epsilon = None
        self.prev = start_position
        self.current = start_position
        self.next = start_position
        self.reset(goal_position)

        self.delay = 0
        self.life = 0

        self.init_super_param()

    def set_world(self, world):
        self.world = world

    def set_goal(self, goal_position):
        self.goal = goal_position

    def init_super_param(self):
        self.epsilon = Args.epsilon
        self.gamma = Args.gamma
        self.epsilon_decrement = Args.epsilon_decrement

    def reset(self, goal_position: tuple[int, int]):
        self.goal = goal_position
        self.is_alive = True
        # shouldn't move to more
        self.life = int((abs(goal_position[0] - self.current[0]) + abs(goal_position[1] - self.current[1])) * 1.5)

    def get_action(self):
        if rd.random() < self.epsilon:
            return rd.choice(Action.LIST)
        # return rd.choice(Action.LIST)
        # return best action
        # Use the loaded model to predict the Q-values for the current state
        q_values = loaded_model.predict(np.array([self.get_state()]), verbose=0)[0]
        #print(q_values)
        # Return the action with the highest Q-value
        tmp = np.argmax(q_values)
        next_pos = self.get_next_position(int(tmp))
        if not self.is_valid_position(next_pos):
            tmp = rd.choice(Action.LIST)
        return tmp

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.world.num_column and 0 <= y < self.world.num_row and (
            not position in self.world.prev_matrix) and (not position in self.world.next_matrix)

    def move(self, action: int):
        self.world.remove_prev_matrix(self.prev)
        self.prev = self.next
        self.world.add_prev_matrix(self.prev, self)

        next_pos = self.get_next_position(action)
        if not self.is_valid_position(next_pos):
            return

        self.world.remove_next_matrix(self.next)
        self.next = next_pos
        self.world.add_next_matrix(self.next, self)

        self.move_state = MoveState.MOVING

    def get_next_position(self, action: int):
        if action == Action.UP:
            return self.prev[0], self.prev[1] - 1
        elif action == Action.DOWN:
            return self.prev[0], self.prev[1] + 1
        elif action == Action.LEFT:
            return self.prev[0] - 1, self.prev[1]
        elif action == Action.RIGHT:
            return self.prev[0] + 1, self.prev[1]
        return self.prev

    def update(self, delay=0.1):
        if self.delay > 0:
            self.delay -= delay
            return
        else:
            self.delay = 0
        if self.move_state == MoveState.IDLE:

            if self.next == self.goal:
                new_goal = self.world.generate_random_empty_position()
                self.set_goal(new_goal)
                self.delay = rd.randint(1, 10) * delay

            action = self.get_action()
            self.move(action)
        elif self.move_state == MoveState.MOVING:
            self.moving()

    def moving(self, step=STEP):
        direct = self.next[0] - self.prev[0], self.next[1] - self.prev[1]
        if self.isEqual(self.current, self.next):
            self.move_state = MoveState.IDLE
        else:
            self.current = self.current[0] + direct[0] * step, self.current[1] + direct[1] * step

    @staticmethod
    def isEqual(coord1: tuple[float, float], coord2: tuple[float, float]):
        return abs(coord1[0] - coord2[0]) < 0.0001 and abs(coord1[1] - coord2[1]) < 0.0001

    def step(self, action) -> tuple[float, bool]:
        self.life -= 1.0

        if self.life <= 0:
            d = abs(self.goal[0] - self.current[0]) + abs(self.goal[1] - self.current[1])
            return -2.0 * (1 + d/(self.world.num_row + self.world.num_column)), True

        next_pos = self.get_next_position(action)
        if not self.is_valid_position(next_pos):
            return -0.2, False

        if self.isEqual(next_pos, self.goal):
            return 10.0, True

        return -0.1, False

    def get_state(self) -> list[int]:
        state = [0, 0, 0, 0, 0, 0]

        state[0] = self.goal[0] - self.current[0]
        state[1] = self.goal[1] - self.current[1]

        for i in range(len(Action.DIRECT)):
            d = Action.DIRECT[i]
            if d[0] == 0 and d[1] == 0:
                continue
            x = self.current[0] + d[0]
            y = self.current[1] + d[1]
            if (x, y) in self.world.prev_matrix:
                state[i + 2] = 1
            if (x, y) in self.world.next_matrix:
                state[i + 2] = 2

        return state
