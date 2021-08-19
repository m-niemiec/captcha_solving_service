import logging
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class PrepareData:
    def __init__(self, data_dir, image_format, captcha_set_to_train):
        self.image_format = image_format
        self.captcha_set_to_train = captcha_set_to_train

        # Get list of all the images
        images = sorted(list(map(str, list(data_dir.glob(f"*.{image_format}")))))
        labels = [img.split(os.path.sep)[-1].split(f".{image_format}")[0] for img in images]
        characters = set(char for label in labels for char in label)

        logging.info("Number of images found: ", len(images))
        logging.info("Number of labels found: ", len(labels))
        logging.info("Number of unique characters: ", len(characters))
        logging.info("Characters present: ", characters)

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

        _, ax = plt.subplots(4, 4, figsize=(10, 5))
        for batch in self.train_dataset.take(1):
            images = batch["image"]
            labels = batch["label"]
            for i in range(16):
                img = (images[i] * 255).numpy().astype("uint8")
                label = tf.strings.reduce_join(self.num_to_char(labels[i])).numpy().decode("utf-8")
                ax[i // 4, i % 4].imshow(img[:, :, 0].T, cmap="gray")
                ax[i // 4, i % 4].set_title(label)
                ax[i // 4, i % 4].axis("off")

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
        label = self.char_to_num(tf.strings.unicode_split(label, input_encoding="UTF-8"))
        # 7. Return a dict as our model is expecting two inputs
        return {"image": img, "label": label}

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


class CTCLayer(layers.Layer):
    def __init__(self, name=None):
        super().__init__(name=name)
        self.loss_fn = keras.backend.ctc_batch_cost

    def call(self, y_true, y_pred):
        # Compute the training-time loss value and add it
        # to the layer using `self.add_loss()`.
        batch_len = tf.cast(tf.shape(y_true)[0], dtype="int64")
        input_length = tf.cast(tf.shape(y_pred)[1], dtype="int64")
        label_length = tf.cast(tf.shape(y_true)[1], dtype="int64")

        input_length = input_length * tf.ones(shape=(batch_len, 1), dtype="int64")
        label_length = label_length * tf.ones(shape=(batch_len, 1), dtype="int64")

        loss = self.loss_fn(y_true, y_pred, input_length, label_length)
        self.add_loss(loss)

        # At test time, just return the computed predictions
        return y_pred


class BuildModel(PrepareData):
    def build_model(self):
        # Inputs to the model
        input_img = layers.Input(
            shape=(self.img_width, self.img_height, 1), name="image", dtype="float32"
        )
        labels = layers.Input(name="label", shape=(None,), dtype="float32")

        # First conv block
        x = layers.Conv2D(
            32,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv1",
        )(input_img)
        x = layers.MaxPooling2D((2, 2), name="pool1")(x)

        # Second conv block
        x = layers.Conv2D(
            64,
            (3, 3),
            activation="relu",
            kernel_initializer="he_normal",
            padding="same",
            name="Conv2",
        )(x)
        x = layers.MaxPooling2D((2, 2), name="pool2")(x)

        # We have used two max pool with pool size and strides 2.
        # Hence, downsampled feature maps are 4x smaller. The number of
        # filters in the last layer is 64. Reshape accordingly before
        # passing the output to the RNN part of the model
        new_shape = ((self.img_width // 4), (self.img_height // 4) * 64)
        x = layers.Reshape(target_shape=new_shape, name="reshape")(x)
        x = layers.Dense(64, activation="relu", name="dense1")(x)
        x = layers.Dropout(0.2)(x)

        # RNNs
        x = layers.Bidirectional(layers.LSTM(128, return_sequences=True, dropout=0.25))(x)
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.25))(x)

        # Output layer
        x = layers.Dense(
            len(self.char_to_num.get_vocabulary()) + 1, activation="softmax", name="dense2", kernel_initializer='he_normal'
        )(x)

        # Add CTC layer for calculating CTC loss at each step
        output = CTCLayer(name="ctc_loss")(labels, x)

        # Define the model
        model = keras.models.Model(
            inputs=[input_img, labels], outputs=output, name="ocr_model_v1"
        )

        # Old optimizer
        # opt = keras.optimizers.Adam()

        # New optimizer
        sgd = keras.optimizers.SGD(learning_rate=0.002,
                                   decay=1e-6,
                                   momentum=0.9,
                                   nesterov=True,
                                   clipnorm=5)

        # Compile the model and return
        model.compile(optimizer=sgd)

        return model


class TrainModel(PrepareData):
    prediction_model = None

    def train_model(self, model):
        epochs = 250
        early_stopping_patience = 50
        # Add early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=early_stopping_patience, restore_best_weights=True
        )

        # Train the model
        history = model.fit(
            self.train_dataset,
            validation_data=self.validation_dataset,
            epochs=epochs,
            callbacks=[early_stopping],
        )

        # Get the prediction model by extracting layers till the output layer
        self.prediction_model = keras.models.Model(
            model.get_layer(name="image").input, model.get_layer(name="dense2").output
        )
        self.prediction_model.summary()

        model.save(f"{self.captcha_set_to_train}.h5")

        return self.prediction_model


class CheckModelAccuracy(TrainModel):
    # A utility function to decode the output of the network
    def decode_batch_predictions(self, pred):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        # Use greedy search. For complex tasks, you can use beam search
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
            :, :self.max_length
        ]
        # Iterate over the results and get back the text
        output_text = []
        for res in results:
            res = tf.strings.reduce_join(self.num_to_char(res)).numpy().decode("utf-8")
            output_text.append(res)
        return output_text

    def show_validation_dataset(self, trained_model):
        #  Let's check results on some validation samples
        for batch in self.validation_dataset.take(1):
            batch_images = batch["image"]
            batch_labels = batch["label"]

            preds = trained_model.predict(batch_images)
            pred_texts = self.decode_batch_predictions(preds)

            orig_texts = []
            for label in batch_labels:
                label = tf.strings.reduce_join(self.num_to_char(label)).numpy().decode("utf-8")
                orig_texts.append(label)

            _, ax = plt.subplots(4, 4, figsize=(15, 5))
            for i in range(len(pred_texts)):
                img = (batch_images[i, :, :, 0] * 255).numpy().astype(np.uint8)
                img = img.T
                title = f"Prediction: {pred_texts[i]}"
                ax[i // 4, i % 4].imshow(img, cmap="gray")
                ax[i // 4, i % 4].set_title(title)
                ax[i // 4, i % 4].axis("off")
        plt.show()


"""
!!! IMPORTANT !!!
This Keras Captcha OCR code was originally written and developed by A_K_Nain.
He kindly published it on keras.io website under this link - https://keras.io/examples/vision/captcha_ocr/
Here is his Twitter link - https://twitter.com/A_K_Nain
Thank you very much for sharing your code and knowledge!

I did only some minor changes and refactored code a little bit so it could be divided into classes.
"""


def main():
    # Name of data set to train
    captcha_set_to_train = 'captcha_type_b'
    # Path to the data set to train
    data_dir = Path(f"./captcha_data_sets/{captcha_set_to_train}")
    # Image format
    image_format = 'jpeg'

    arguments = (data_dir, image_format, captcha_set_to_train)

    # Get the model
    model = BuildModel(*arguments).build_model()
    model.summary()

    # Train Model
    trained_model = TrainModel(*arguments).train_model(model)

    # Present Model Accuracy
    CheckModelAccuracy(*arguments).show_validation_dataset(trained_model)


if __name__ == '__main__':
    main()
