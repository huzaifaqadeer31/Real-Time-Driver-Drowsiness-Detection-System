import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt

from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.applications.efficientnet import preprocess_input
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

print("TensorFlow version:", tf.__version__)

data_path   = "/kaggle/input/driver-drowsiness-detection-system-dataset/0 FaceImages"
save_path   = "/kaggle/working"
image_size  = (224, 224)
batch_size  = 32
num_epochs  = 15
num_classes = 2

augmentation = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    validation_split=0.2,
    rotation_range=20,
    zoom_range=0.2,
    width_shift_range=0.2,
    height_shift_range=0.2,
    brightness_range=[0.7, 1.3],
    horizontal_flip=True,
    shear_range=0.15,
    fill_mode="nearest"
)
val_prep = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    validation_split=0.2
)
train_data = augmentation.flow_from_directory(
    data_path,
    target_size=image_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="training",
    shuffle=True
)
val_data = val_prep.flow_from_directory(
    data_path,
    target_size=image_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation",
    shuffle=False
)

print("Classes found:", train_data.class_indices)
base = EfficientNetB0(
    weights="imagenet",
    include_top=False,
    input_shape=(224, 224, 3)
)
base.trainable = True
for layer in base.layers[:-100]:
    layer.trainable = False

x      = base.output
x      = GlobalAveragePooling2D()(x)
x      = Dense(256, activation="relu")(x)
x      = Dropout(0.5)(x)
x      = Dense(64, activation="relu")(x)
x      = Dropout(0.3)(x)
output = Dense(num_classes, activation="softmax")(x)

model = Model(inputs=base.input, outputs=output)

model.compile(
    optimizer=Adam(1e-4),
    loss="categorical_crossentropy",
    metrics=["accuracy"]
)
model.summary()
save_best = ModelCheckpoint(
    os.path.join(save_path, "drowsiness_best.keras"),
    monitor="val_accuracy",
    save_best_only=True,
    mode="max"
)
stop_early = EarlyStopping(
    monitor="val_loss",
    patience=7,
    restore_best_weights=True
)
history = model.fit(
    train_data,
    validation_data=val_data,
    epochs=num_epochs,
    callbacks=[save_best, stop_early]
)
model.save(os.path.join(save_path, "drowsiness_final.keras"))
print("model saved successfully")

predictions = model.predict(val_gen)

y_pred = np.argmax(predictions, axis=1)
y_true = val_gen.classes

cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=list(train_gen.class_indices.keys()),
    yticklabels=list(train_gen.class_indices.keys())
)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.show()

print("\nClassification Report:\n")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=list(train_gen.class_indices.keys())
    )
)
print(f"\nPrecision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1 Score  : {f1:.4f}")
plt.figure(figsize=(10, 5))

plt.plot(history.history["accuracy"], label="Train Accuracy")
plt.plot(history.history["val_accuracy"], label="Validation Accuracy")
plt.title("Training and Validation Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend()
plt.grid()
plt.show()


plt.figure(figsize=(10, 5))

plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.title("Training and Validation Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.legend()
plt.grid()
plt.show()