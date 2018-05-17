from __future__ import print_function, division

from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten, Dropout, multiply
from keras.layers import BatchNormalization, Activation, Embedding, ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.models import Sequential, Model
from keras.optimizers import Adam
from model import train, save_model, build_audio_generator, build_audio_discriminator
from optparse import OptionParser
import uuid
from tqdm import tqdm
import librosa
import tensorflow as tf

import matplotlib.pyplot as plt

import numpy as np

def main():

    parser = OptionParser()

    # Only required for labeling - Defines train or generate mode
    parser.add_option('-m', '--mode', help='train or gen', dest='mode', default = 'label')
    # Only required for labeling - Enter Model id here
    parser.add_option('-u', '--uid', help='enter model id here')

    epochs = 10000

    (options, args) = parser.parse_args()

    training_data_path = 'data/cv-valid-train/*.wav'

    if options.mode == 'train':
        frame_size = 500
        frame_shift = 128

        num_classes = 1

        audio_shape_disc = (frame_size,256)

        optimizer = Adam(0.0002, 0.5)
        losses = ['binary_crossentropy']

        # Build and compile the discriminator
        audio_discriminator = build_audio_discriminator(audio_shape_disc)
        audio_discriminator.compile(loss=losses, optimizer=optimizer, metrics=['accuracy'])

        # Build the generator
        audio_generator = build_audio_generator(frame_size)

        # The generator takes noise
        noise = Input(shape=(frame_size, 1))

        audio = audio_generator(noise)

        # For the combined model we will only train the generator
        audio_discriminator.trainable = False

        # The discriminator takes generated audio as input and determines validity
        audio_valid = audio_discriminator(audio)

        # The combined model  (stacked generator and discriminator) takes
        # noise as input => generates audio => determines validity
        audio_combined = Model(noise, audio_valid)
        audio_combined.compile(loss=losses, optimizer=optimizer)

        train(audio_generator, audio_discriminator, audio_combined, epochs, frame_size, frame_shift)

if __name__ == '__main__':
    main()
