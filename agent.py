from config import *
import random as rd

STEP = 0.2


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
        self.reset(start_position, goal_position)

        self.delay = 0

        self.init_super_param()

    def set_world(self, world):
        self.world = world

    def set_goal(self, goal_position):
        self.goal = goal_position

    def init_super_param(self):
        self.epsilon = Args.epsilon
        self.gamma = Args.gamma
        self.epsilon_decrement = Args.epsilon_decrement

    def reset(self, start_position: tuple[int, int], goal_position: tuple[int, int]):
        self.prev = start_position
        self.current = start_position
        self.next = start_position
        self.goal = goal_position
        self.is_alive = True

    def get_action(self):
        if rd.random() < self.epsilon:
            return rd.choice(Action.LIST)
        return rd.choice(Action.LIST)

    def is_valid_position(self, position):
        x, y = position
        return 0 <= x < self.world.num_row and 0 <= y < self.world.num_column and (
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
                print("Nice")

            action = self.get_action()
            self.move(action)
        elif self.move_state == MoveState.MOVING:
            self.moving()

    def moving(self):
        direct = self.next[0] - self.prev[0], self.next[1] - self.prev[1]
        if abs(self.current[0] - self.next[0]) < 0.01 and abs(self.current[1] - self.next[1]) < 0.01:
            self.move_state = MoveState.IDLE
        else:
            self.current = self.current[0] + direct[0] * STEP, self.current[1] + direct[1] * STEP