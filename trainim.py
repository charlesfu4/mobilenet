from __future__ import print_function
import os
from keras import backend as K
from loadim import load_images
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint,TensorBoard
from keras.optimizers import SGD
from clr_callback import CyclicLR
import numpy as np
import pandas as pd
from clr import OneCycleLR
from mobilenets import MiniMobileNetV2
#Tensorboard callback for cyclical learning rate
class LRTensorBoard(TensorBoard):
    def __init__(self, log_dir):  # add other arguments to __init__ if you need
        super().__init__(log_dir=log_dir)

    def on_epoch_end(self, epoch, logs=None):
        logs.update({'lr': K.eval(self.model.optimizer.lr)})
        super().on_epoch_end(epoch, logs)

#load datasets from tiny imagenet floder
X_train,Y_train,X_test,Y_test = load_images('./', 200)
#one-hot encoding for labels data
Y_train = pd.get_dummies(Y_train)
Y_test = pd.get_dummies(Y_test)
data_augmentation = False
batch_size = 64
nb_classes = 200
nb_epoch = 20  
num_samples = X_train.shape[0]
img_rows = 64
img_cols = 64
img_channels = 3
lr_manager = OneCycleLR(max_lr=1, maximum_momentum=0.9, verbose=True)
#lr_manager = CyclicLR(base_lr=0.025, max_lr=0.1, step_size = 4*X_train.shape[0]//batch_size, mode = 'triangular')

# For training, the auxilary branch must be used to correctly train NASNet
model = MiniMobileNetV2((img_rows, img_cols, img_channels),
                        alpha=1,
                        dropout=0.4,
                        weight_decay=1e-6,
                        weights=None,
                        classes=nb_classes)
model.summary()

# These values will be overridden by the above callback
optimizer = SGD(lr=0.004, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])



if not data_augmentation:
    print('Not using data augmentation.')
    model.fit(
        X_train,
        Y_train,
        batch_size=batch_size,
        epochs=nb_epoch,
        validation_data=(X_test, Y_test),
        shuffle=True,
        verbose=1,
        callbacks=[LRTensorBoard(log_dir='./Graph/5'),lr_manager])
else:
    print('Using real-time data augmentation.')
    # This will do preprocessing and realtime data augmentation:
    datagen = ImageDataGenerator(
        featurewise_center=False,  # set input mean to 0 over the dataset
        samplewise_center=False,  # set each sample mean to 0
        featurewise_std_normalization=False,  # divide inputs by std of the dataset
        samplewise_std_normalization=False,  # divide each input by its std
        zca_whitening=False,  # apply ZCA whitening
        # randomly rotate images in the range (degrees, 0 to 180)
        rotation_range=30,
        # randomly shift images horizontally (fraction of total width)
        width_shift_range=0,
        # randomly shift images vertically (fraction of total height)
        height_shift_range=0,
        horizontal_flip=True,  # randomly flip images
        vertical_flip=False)  # randomly flip images

    # Compute quantities required for featurewise normalization
    # (std, mean, and principal components if ZCA whitening is applied).
    datagen.fit(X_train)

    # Fit the model on the batches generated by datagen.flow().
    model.fit_generator(
        datagen.flow(X_train, Y_train, batch_size=batch_size, shuffle=True),
        steps_per_epoch=X_train.shape[0] // batch_size,
        validation_data=(X_test, Y_test),
        epochs=nb_epoch,
        verbose=1,
        callbacks=[LRTensorBoard(log_dir='./Graph/3'), lr_manager])
    