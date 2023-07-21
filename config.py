class Args:
    epsilon = 0.8
    gamma = 0.9
    epsilon_decrement = 0.5
    num_action = 5
    num_column = 7
    num_row = 7
    state_dimension = 65
    num_agent = 5

    num_epochs = 4000
    learning_rate = 0.001
    sync_rate = 40
    replay_size = 10000
    batch_size = 64
    patient_factor = 10
    warmup_steps = 1000


class Action:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    STATIC = 4
    LIST = [UP, DOWN, LEFT, RIGHT, STATIC]
