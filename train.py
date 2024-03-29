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
import os
import sys

# noinspection PyFromFutureImport
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import save_model, load_model


def create_q_model(input_shape, num_acts):
    model = Sequential([
        Dense(32, activation='relu', input_shape=input_shape),
        Dense(64, activation='relu'),
        Dense(num_acts, activation='linear')
    ])
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
    return model


def export_time_to_HMS(time_data: float):
    time_data = int(time_data)
    h = int(time_data / 3600)
    time_data %= 3600
    m = int(time_data / 60)
    time_data %= 60
    s = time_data
    result = ""
    if h >= 10:
        result += str(h)
    else:
        result += "0" + str(h)
    result += ":"
    if m >= 10:
        result += str(m)
    else:
        result += "0" + str(m)
    result += ":"
    if s >= 10:
        result += str(s)
    else:
        result += "0" + str(s)
    return result


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
saved_file_name = Args.save_model
if Args.is_using_previous_model:
    q_model = load_model(Args.previous_training_file)
else:
    q_model = create_q_model(state_shape, num_actions)

curr = time.time()
final_reward = 0
rate_complete = 0

for j in range(1, len(my_world.agents)):
    my_world.agents[j].epsilon = 1
    my_world.agents[j].set_speed(1)

my_world.agents[0].set_speed(1)

sum_time = 0

for i in range(Args.num_epochs):
    agent = my_world.agents[0]
    agent.reset(my_world.generate_random_position_with_distance(agent.prev, 3))
    done = False
    sum_reward = 0
    st_time = time.time()

    while not done:
        for j in range(1, len(my_world.agents)):
            action = my_world.agents[j].get_action()
            # Agent move
            agent.move(action)
            agent.moving()

        state = agent.get_state()

        if np.random.rand() < 0.01:
            action = agent.get_action_2(q_model)
        else:
            action = agent.get_action(q_model)

        reward, done = agent.step(action)

        # Agent move
        agent.move(action)
        agent.moving()

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
    if agent.epsilon > epsilon_min:
        agent.epsilon *= epsilon_decay

    final_reward += sum_reward

    ed_time = time.time()
    if i % 7 == 0:
        sum_time = ed_time - st_time
    else:
        sum_time += ed_time - st_time

    # print("\rEpoch " + str(i) + ": reward = " + str(round(sum_reward, 1)) + ", complete_rate = " +
    # str(round(rate_complete/(i + 1) * 100)) + " %, epsilon: " + str(round(agent.epsilon, 2)), end='\r')
    print(f"\rEpoch:{i + 1}/{Args.num_epochs}----"
          f"time_remaining:{export_time_to_HMS(sum_time / (i % 7 + 1) * (Args.num_epochs - i - 1))}----"
          f"complete_rate:{round(rate_complete / (i + 1) * 100)}%----epsilon:{round(agent.epsilon, 2)}----"
          f"reward:{round(sum_reward, 1)}", end="\n")

    if sum_reward > 0:
        rate_complete += 1

    if i % 500 == 499:
        save_model(q_model, saved_file_name)

save_model(q_model, saved_file_name)

print("Average Reward: " + str(round(final_reward / Args.num_epochs, 3)))
print("Rate: " + str(round(rate_complete * 100 / Args.num_epochs, 3)) + "%")
print("Time: " + str(round((time.time() - curr), 2)) + " s")
