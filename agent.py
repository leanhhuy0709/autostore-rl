import random
from typing import Any
from tensorflow.keras.models import save_model, load_model
from config import Args, Action
import random as rd
import numpy as np

STEP = 0.2

if Args.visualize_model != '':
    loaded_model = load_model(Args.visualize_model)
else:
    load_model = None


class MoveState:
    MOVING = 0
    IDLE = 1


class Agent:
    def __init__(self, start_position: tuple[int, int], goal_position: tuple[int, int]):
        self.world = None
        self.prev = None
        self.current = None
        self.next = None
        self.move_state = MoveState.IDLE
        self._speed = STEP

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

    def set_speed(self, speed: int):
        if speed > 1:
            speed = 1
        elif speed < 0.1:
            speed = 0.1
        self._speed = speed

    def init_super_param(self):
        self.epsilon = Args.epsilon
        self.gamma = Args.gamma
        self.epsilon_decrement = Args.epsilon_decrement

    def reset(self, goal_position: tuple[int, int], delay: int = None, life: int = None):
        self.goal = goal_position

        if delay is None:
            self.delay = 0.1 * random.randint(0, 10)
        else:
            self.delay = delay

        # shouldn't move to more
        if life is None:
            self.life = int(
                (abs(goal_position[0] - self.current[0]) + abs(goal_position[1] - self.current[1])) * 2) + 1
        else:
            self.life = life

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.world.num_column and 0 <= y < self.world.num_row and (
            not position in self.world.prev_matrix) and (not position in self.world.next_matrix)

    def move(self, action: int):
        """
        Set prev and next
        If is not valid move => STAND
        """
        next_pos = self.get_next_position(action)
        if not self.is_valid_position(next_pos):
            return

        self.world.remove_next_matrix(self.next)
        self.next = next_pos
        self.world.add_next_matrix(self.next, self)

        self.move_state = MoveState.MOVING

    def moving(self):
        direct = self.next[0] - self.prev[0], self.next[1] - self.prev[1]
        next_pos = self.current[0] + direct[0] * self._speed, self.current[1] + direct[1] * self._speed

        if self.current[0] <= self.next[0] <= next_pos[0] or self.current[0] >= self.next[0] >= next_pos[0]:
            if self.current[1] <= self.next[1] <= next_pos[1] or self.current[1] >= self.next[1] >= next_pos[1]:
                self.current = self.next
                self.move_state = MoveState.IDLE
                self.world.remove_prev_matrix(self.prev)
                self.prev = self.next
                self.world.add_prev_matrix(self.prev, self)
                return

        self.current = next_pos

    def handle_move(self, time_unit: int = 0.1) -> bool:
        if self.delay > 0:
            self.delay -= time_unit
            return False

        self.delay = 0
        if self.move_state == MoveState.IDLE:
            if self.next == self.goal:
                return True
            action = self.get_action_2()
            self.move(action)
        elif self.move_state == MoveState.MOVING:
            self.moving()
        return False

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

    @staticmethod
    def isEqual(coord1: tuple[float, float], coord2: tuple[float, float]):
        return abs(coord1[0] - coord2[0]) < 0.0001 and abs(coord1[1] - coord2[1]) < 0.0001

    '''
    Edit some function below
    '''

    def step(self, action) -> tuple[float, bool]:
        self.life -= 1.0

        if self.life <= 0:
            d = abs(self.goal[0] - self.current[0]) + abs(self.goal[1] - self.current[1])
            # return -0.1, True
            return -3.0 * (1 + d/(self.world.num_row + self.world.num_column)), True

        next_pos = self.get_next_position(action)
        if not self.is_valid_position(next_pos):
            return -0.5, False

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

    def get_action(self, model=None):
        if rd.random() < self.epsilon:
            return rd.choice(Action.LIST)
        return self.get_best_action(model)

    def get_action_2(self, model=None):
        if rd.random() < self.epsilon:
            return self.get_random_action_with_rate()
        return self.get_best_action(model)

    def get_action_3(self, model=None):
        if rd.random() < self.epsilon:
            my_list = []
            for i in range(4):
                next_pos = self.get_next_position(i)
                if not self.is_valid_position(next_pos):
                    continue
                d1 = abs(next_pos[0] - self.goal[0]) + abs(next_pos[1] - self.goal[1])
                d2 = abs(self.prev[0] - self.goal[0]) + abs(self.prev[1] - self.goal[1])
                if d1 <= d2:
                    my_list.append(i)
            if len(my_list) == 0:
                pass
                # print('Error')

            if len(my_list) > 0:
                return np.random.choice(my_list)
        return self.get_best_action(model)

    @staticmethod
    def get_2_max_index(array):
        idx1 = idx2 = 0
        max1 = max2 = -9999999
        for i in range(len(array)):
            if max1 < array[i]:
                max2 = max1
                idx2 = idx1
                max1 = array[i]
                idx1 = i
            elif max2 < array[i]:
                max2 = array[i]
                idx2 = i
        return idx1, idx2

    def get_random_action_with_rate(self):
        default_rate = [0.2, 0.2, 0.2, 0.2, 0.2]
        curr_rate = 0

        sum_rate = 0.2
        for i in range(4):
            next_pos = self.get_next_position(i)
            if not self.is_valid_position(next_pos):
                default_rate[i] *= 0.1
                sum_rate += default_rate[i]
                continue
            d1 = abs(next_pos[0] - self.goal[0]) + abs(next_pos[1] - self.goal[1])
            d2 = abs(self.current[0] - self.goal[0]) + abs(self.current[1] - self.goal[1])
            if d1 > d2:
                default_rate[i] *= 0.5
            elif d1 < d2:
                default_rate[i] *= 2
            sum_rate += default_rate[i]

        for i in range(5):
            default_rate[i] /= sum_rate

        value = np.random.rand()
        for i in range(4):
            curr_rate += default_rate[i]
            if value <= curr_rate:
                return i
        return Action.STATIC

    def get_best_action(self, model):
        if model is None:
            if loaded_model is None:
                return self.get_random_action_with_rate()
            model = loaded_model

        # Use the loaded model to predict the Q-values for the current state
        q_values = model.predict(np.array([self.get_state()]), verbose=0)[0]

        idx1, idx2 = Agent.get_2_max_index(q_values)

        tmp = idx1

        return tmp
