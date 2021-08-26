import pickle
from io import BytesIO

import keras
import numpy as np
import tensorflow as tf
from PIL import Image
from keras.models import load_model
from tensorflow.keras import layers

from ctc_layer import CTCLayer


class SolveCaptcha:
    image_format = None
    char_to_num = None
    num_to_char = None

    async def get_solution(self, captcha_image):
        trained_model = load_model('trained_models/captcha_type_b.h5', custom_objects={'CTCLayer': CTCLayer})

        self.image_format = 'jpeg'

        stream = BytesIO(await captcha_image.read())
        image = Image.open(stream).convert("RGB")
        stream.close()
        image.save('TEMP_CAPTCHAS/captcha.jpeg', 'JPEG')

        images = ['TEMP_CAPTCHAS/captcha.jpeg']

        with open("trained_models/captcha_type_b.pickle", "rb") as file:
            characters = pickle.load(file)

        prediction_model = keras.models.Model(
            trained_model.get_layer(name="image").input, trained_model.get_layer(name="dense2").output
        )

        self.char_to_num = layers.experimental.preprocessing.StringLookup(
            vocabulary=characters, mask_token=None
        )

        self.num_to_char = layers.StringLookup(
            vocabulary=self.char_to_num.get_vocabulary(), mask_token=None, invert=True
        )

        # Splitting data into training and validation sets
        x_train, x_valid, y_train, y_valid = self.split_data(np.array(images))

        validation_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
        validation_dataset = (
            validation_dataset.map(
                self.encode_single_sample, num_parallel_calls=tf.data.experimental.AUTOTUNE
            ).batch(16).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
        )

        for batch in validation_dataset.take(1):
            batch_images = batch['image']

            preds = prediction_model.predict(batch_images)

            pred_texts = self.decode_batch_predictions(preds)[0]

            return pred_texts

    def encode_single_sample(self, img_path, label):
        img = tf.io.read_file(img_path)
        if self.image_format == 'jpeg':
            img = tf.io.decode_jpeg(img, channels=1)
        elif self.image_format == 'png':
            img = tf.io.decode_png(img, channels=1)
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = tf.image.resize(img, [50, 200])
        img = tf.transpose(img, perm=[1, 0, 2])
        label = self.char_to_num(tf.strings.unicode_split(label, input_encoding='UTF-8'))

        return {'image': img, 'label': label}

    def decode_batch_predictions(self, pred):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        # Use greedy search. For complex tasks, you can use beam search
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :6]
        # Iterate over the results and get back the text
        output_text = []
        for res in results:
            res = tf.strings.reduce_join(self.num_to_char(res)).numpy().decode("utf-8")
            output_text.append(res)

        return output_text

    @staticmethod
    def split_data(images, train_size=0.9, shuffle=True):
        # 1. Get the total size of the dataset
        size = len(images)
        # 2. Make an indices array and shuffle it, if required
        indices = np.arange(size)

        if shuffle:
            np.random.shuffle(indices)
        # 3. Get the size of training samples
        train_samples = int(size * train_size)
        # 4. Split data into training and validation sets
        x_train, y_train = images[indices[:train_samples]], ['']
        x_valid, y_valid = images[indices[train_samples:]], ['']

        return x_train, x_valid, y_train, y_valid
