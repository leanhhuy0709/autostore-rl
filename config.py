class Args:
    epsilon = 1
    gamma = 0.9
    epsilon_decrement = 0.993
    num_action = 5
    num_column = 7
    num_row = 7
    #state_dimension = 65
    num_agent = 5

    num_epochs = 20000
    learning_rate = 0.002
    #sync_rate = 40
    #replay_size = 10000
    batch_size = 64
    #patient_factor = 10
    #warmup_steps = 1000

    is_using_previous_model = False
    previous_training_file = 'trained_model/trained_model_11.h5'

    visualize_model = 'trained_model/trained_model_11.h5'
    save_model = 'trained_model/trained_model_12.h5'

    cell_size = 30
    border_size = 2


class Action:
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    STATIC = 4
    LIST = [UP, DOWN, LEFT, RIGHT, STATIC]
    DIRECT = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]
