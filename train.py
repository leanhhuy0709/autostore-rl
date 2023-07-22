"""
Edit all below
"""

import tensorflow as tf
from world import World, Action
from config import Args
import time
import numpy as np
from collections import deque
import random

# noinspection PyFromFutureImport
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import save_model, load_model


def create_q_model(input_shape, num_acts):
    model = Sequential([
        Dense(32, activation='relu', input_shape=input_shape),
        Dense(32, activation='relu'),
        Dense(num_acts, activation='linear')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    return model


# Q-learning parameters
gamma = Args.gamma  # Discount factor
epsilon = Args.epsilon  # Exploration rate
epsilon_min = 0.01
epsilon_decay = Args.epsilon_decrement
batch_size = Args.batch_size

# Initialize experience replay buffer
experience_replay_buffer = deque(maxlen=10000)

my_world = World()

state_shape = (6,)
num_actions = len(Action.LIST)

# Create the Q-network
#q_model = create_q_model(state_shape, num_actions)
q_model = load_model(Args.model_filename)

curr = time.time()
final_reward = 0
rate_complete = 0

for j in range(1, len(my_world.agents)):
    my_world.agents[j].epsilon = 1

for i in range(Args.num_epochs):
    agent = my_world.agents[0]
    agent.reset(my_world.generate_random_empty_position())
    done = False
    sum_reward = 0

    while not done:
        for j in range(1, len(my_world.agents)):
            action = my_world.agents[j].get_action()
            # Agent move
            agent.move(action)
            agent.moving(1)

        state = agent.get_state()

        if np.random.rand() <= epsilon:
            action = np.random.choice(num_actions)
        else:
            q_values = q_model.predict(np.array([state]), verbose=0)[0]
            action = np.argmax(q_values)

        reward, done = agent.step(action)

        # Agent move
        agent.move(action)
        agent.moving(1)

        sum_reward += reward

        # Update Q-values using Q-learning
        next_state = agent.get_state()
        experience_replay_buffer.append((state, action, reward, next_state, done))

        if len(experience_replay_buffer) >= batch_size:
            batch = random.sample(experience_replay_buffer, batch_size)
            states_batch, actions_batch, rewards_batch, next_states_batch, done_batch = zip(*batch)

            states_batch = np.stack(states_batch)
            actions_batch = np.array(actions_batch, dtype=int)
            rewards_batch = np.array(rewards_batch, dtype=float)
            next_states_batch = np.stack(next_states_batch)
            done_batch = np.array(done_batch, dtype=bool)

            q_values_next = q_model.predict_on_batch(next_states_batch)
            targets_batch = rewards_batch + (1 - done_batch) * gamma * np.amax(q_values_next, axis=1)

            q_values_current = q_model.predict_on_batch(states_batch)
            q_values_current[np.arange(batch_size), actions_batch] = targets_batch

            # Train the Q-network on the current batch
            q_model.train_on_batch(states_batch, q_values_current)

    # Decay exploration rate
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

    print("Epoch " + str(i) + ": " + str(sum_reward))
    final_reward += sum_reward
    if sum_reward > 0:
        rate_complete += 1

model_filename = Args.model_filename
save_model(q_model, model_filename)

print("Average Reward: " + str(round(final_reward/Args.num_epochs, 3)))
print("Rate: " + str(round(rate_complete * 100/Args.num_epochs, 3)) + "%")
print("Time: " + str(round((time.time() - curr) * 1000, 2)) + " ms")
