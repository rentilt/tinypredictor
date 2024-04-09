from model import get_model
import numpy as np
from sklearn.model_selection import train_test_split 

BS = 32
EPOCHS = 100

def train():
    model = get_model()

    X = np.load('dataset.npy')
    y = np.load('targets.npy')
    X = X.reshape((X.shape[0], X.shape[1], X.shape[2], 1))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15)
    print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

    model.fit(X_train, y_train, batch_size=BS, epochs=EPOCHS, validation_split=0.15)

    score = model.evaluate(X_test, y_test, verbose=0)
    print("Test loss:", score[0])
    print("Test accuracy:", score[1])

train()