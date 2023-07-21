'''
import tensorflow as tf
from world import World, Action
from config import Args

# Create the policy network
policy = tf.keras.Sequential([
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(64, activation='relu'),
  tf.keras.layers.Dense(len(Action.LIST), activation='softmax')
])

# Create the value network
value = tf.keras.Sequential([
  tf.keras.layers.Dense(128, activation='relu'),
  tf.keras.layers.Dense(64, activation='relu'),
  tf.keras.layers.Dense(1, activation='linear')
])

# Initialize the optimizer
optimizer = tf.keras.optimizers.Adam(learning_rate=Args.learning_rate)

# Define the loss function
loss = tf.keras.losses.MeanSquaredError()

print(policy([1, 2, 3, 4, 5]))



# Define the training loop
for i in range(10000):
  # Get a state from the environment
  state = env.reset()

  # Select an action from the policy network
  action = policy(state)

  # Take the action in the environment and get a reward
  next_state, reward, done, _ = env.step(action)

  # Update the policy network
  with tf.GradientTape() as tape:
    # Calculate the value of the current state
    v = value(state)

    # Calculate the value of the next state
    v_next = value(next_state)

    # Calculate the advantage
    advantage = reward + gamma * v_next - v

    # Calculate the loss
    loss = loss(advantage, policy(state))

  # Update the policy network
  grads = tape.gradient(loss, policy.trainable_variables)
  optimizer.apply_gradients(zip(grads, policy.trainable_variables))

  # If the episode is over, reset the environment
  if done:
    state = env.reset()

# Save the policy network
policy.save('policy.h5')'''