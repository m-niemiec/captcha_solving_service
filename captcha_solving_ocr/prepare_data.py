import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers


class PrepareData:
    def __init__(self, data_dir, image_format, captcha_set_to_train):
        self.image_format = image_format
        self.captcha_set_to_train = captcha_set_to_train

        # Get list of all the images
        images = sorted(list(map(str, list(data_dir.glob(f'*.{image_format}')))))
        labels = [img.split(os.path.sep)[-1].split(f'.{image_format}')[0] for img in images]
        characters = set(char for label in labels for char in label)

        logging.info('Number of images found: ', len(images))
        logging.info('Number of labels found: ', len(labels))
        logging.info('Number of unique characters: ', len(characters))
        logging.info('Characters present: ', characters)

        # Batch size for training and validation
        batch_size = 16

        # Desired image dimensions
        self.img_width = 200
        self.img_height = 50

        # Factor by which the image is going to be downsampled
        # by the convolutional blocks. We will be using two
        # convolution blocks and each block will have
        # a pooling layer which downsample the features by a factor of 2.
        # Hence total downsampling factor would be 4.

        # Maximum length of any captcha in the dataset
        self.max_length = max([len(label) for label in labels])

        # Mapping characters to integers
        self.char_to_num = layers.experimental.preprocessing.StringLookup(
            vocabulary=list(characters), mask_token=None
        )

        # Mapping integers back to original characters
        self.num_to_char = layers.experimental.preprocessing.StringLookup(
            vocabulary=self.char_to_num.get_vocabulary(), mask_token=None, invert=True
        )

        # Splitting data into training and validation sets
        x_train, x_valid, y_train, y_valid = self.split_data(np.array(images), np.array(labels))

        train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
        self.train_dataset = (
            train_dataset.map(
                self.encode_single_sample, num_parallel_calls=tf.data.experimental.AUTOTUNE
            ).batch(batch_size).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
        )

        validation_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
        self.validation_dataset = (
            validation_dataset.map(
                self.encode_single_sample, num_parallel_calls=tf.data.experimental.AUTOTUNE
            ).batch(batch_size).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
        )

    def show_train_data_set(self):
        _, ax = plt.subplots(4, 4, figsize=(10, 5))
        for batch in self.train_dataset.take(1):
            images = batch['image']
            labels = batch['label']
            for i in range(16):
                img = (images[i] * 255).numpy().astype('uint8')
                label = tf.strings.reduce_join(self.num_to_char(labels[i])).numpy().decode('utf-8')
                ax[i // 4, i % 4].imshow(img[:, :, 0].T, cmap='gray')
                ax[i // 4, i % 4].set_title(label)
                ax[i // 4, i % 4].axis('off')

        plt.show()

    def encode_single_sample(self, img_path, label):
        # 1. Read image
        img = tf.io.read_file(img_path)
        # 2. Decode and convert to grayscale
        if self.image_format == 'jpeg':
            img = tf.io.decode_jpeg(img, channels=1)
        elif self.image_format == 'png':
            img = tf.io.decode_png(img, channels=1)
        # 3. Convert to float32 in [0, 1] range
        img = tf.image.convert_image_dtype(img, tf.float32)
        # 4. Resize to the desired size
        img = tf.image.resize(img, [self.img_height, self.img_width])
        # 5. Transpose the image because we want the time
        # dimension to correspond to the width of the image.
        img = tf.transpose(img, perm=[1, 0, 2])
        # 6. Map the characters in label to numbers
        label = self.char_to_num(tf.strings.unicode_split(label, input_encoding='UTF-8'))

        # 7. Return a dict as our model is expecting two inputs
        return {'image': img, 'label': label}

    @staticmethod
    def split_data(images, labels, train_size=0.9, shuffle=True):
        # 1. Get the total size of the dataset
        size = len(images)
        # 2. Make an indices array and shuffle it, if required
        indices = np.arange(size)

        if shuffle:
            np.random.shuffle(indices)
        # 3. Get the size of training samples
        train_samples = int(size * train_size)
        # 4. Split data into training and validation sets
        x_train, y_train = images[indices[:train_samples]], labels[indices[:train_samples]]
        x_valid, y_valid = images[indices[train_samples:]], labels[indices[train_samples:]]

        return x_train, x_valid, y_train, y_valid
