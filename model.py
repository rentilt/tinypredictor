from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPooling2D, Flatten
import tensorflow as tf 

def get_model():
    model = Sequential()

    # convolution 
    model.add(Conv2D(64, kernel_size=(3,3), strides=(1,1), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))

    # fc
    model.add(Flatten())
    model.add(Dense(2048, activation='relu'))
    model.add(Dense(1024, activation='relu'))
    model.add(Dense(512, activation='relu'))

    # output layer
    model.add(Dense(2, activation='log_softmax'))
    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), optimizer="adam", metrics=["accuracy"])

    return model