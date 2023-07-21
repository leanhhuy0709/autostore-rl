from tensorflow.keras.models import save_model, load_model
model_filename = "trained_model.h5"
loaded_model = load_model(model_filename)

print(loaded_model)