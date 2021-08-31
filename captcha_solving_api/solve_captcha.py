import os
import pickle

import keras
import numpy as np
import tensorflow as tf
from fastapi import HTTPException
from fastapi_sqlalchemy import db
from keras.models import load_model
from tensorflow.keras import layers

from ctc_layer import CTCLayer
from models import CaptchaSolveQuery as ModelCaptchaSolveQuery, User as ModelUser


class SolveCaptcha:
    image_format = None
    char_to_num = None
    num_to_char = None

    async def get_solution(self, user_id, image_format: str, image_path: str, captcha_type: int, image_metadata: str) -> str:
        self.image_format = image_format

        trained_model, characters, captcha_length = await self.load_proper_model_characters(captcha_type)

        images = [image_path]

        prediction_model = keras.models.Model(
            trained_model.get_layer(name='image').input, trained_model.get_layer(name='dense2').output
        )

        self.char_to_num = layers.experimental.preprocessing.StringLookup(
            vocabulary=characters, mask_token=None
        )

        self.num_to_char = layers.StringLookup(
            vocabulary=self.char_to_num.get_vocabulary(), mask_token=None, invert=True
        )

        # Splitting data into training and validation sets
        x_train, x_valid, y_train, y_valid = await self.split_data(np.array(images))

        validation_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
        validation_dataset = (
            validation_dataset.map(
                self.encode_single_sample, num_parallel_calls=tf.data.experimental.AUTOTUNE
            ).batch(16).prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
        )

        for batch in validation_dataset.take(1):
            batch_images = batch['image']

            prediction = prediction_model.predict(batch_images)

            prediction_text = self.decode_batch_predictions(prediction, captcha_length)[0]

            os.remove(image_path)

            if '[UNK]'*2 in prediction_text:
                raise HTTPException(status_code=400, detail='Oops! It seems that the image you passed is not our '
                                                            'supported captcha type (or it\'s not captcha at all).'
                                                            'Credits weren\'t taken from your account.')
            elif '[UNK]' in prediction_text:
                raise HTTPException(status_code=400, detail='Oops! It seems that this captcha is really hard to solve,'
                                                            'please send another one. Credits weren\'t taken from your'
                                                            'account.')
            else:
                await self.add_captcha_solve_query(user_id, captcha_type, image_metadata, prediction_text)
                await self.reduce_user_credit_balance(user_id)

                return prediction_text

    def encode_single_sample(self, img_path, label):
        img = tf.io.read_file(img_path)

        if self.image_format == 'jpeg' or self.image_format == 'jpg':
            img = tf.io.decode_jpeg(img, channels=1)
        elif self.image_format == 'png':
            img = tf.io.decode_png(img, channels=1)

        img = tf.image.convert_image_dtype(img, tf.float32)
        img = tf.image.resize(img, [50, 200])
        img = tf.transpose(img, perm=[1, 0, 2])
        label = self.char_to_num(tf.strings.unicode_split(label, input_encoding='UTF-8'))

        return {'image': img, 'label': label}

    def decode_batch_predictions(self, pred, captcha_length):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        # Use greedy search. For complex tasks, you can use beam search
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :captcha_length]
        # Iterate over the results and get back the text
        output_text = []
        for res in results:
            res = tf.strings.reduce_join(self.num_to_char(res)).numpy().decode('utf-8')
            output_text.append(res)

        return output_text

    @staticmethod
    async def split_data(images, train_size=0.9, shuffle=True):
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

    @staticmethod
    async def load_proper_model_characters(captcha_type: int) -> tuple[keras.models.Model, list, int]:
        if captcha_type == 0:
            trained_model = load_model('trained_models/captcha_type_a.h5', custom_objects={'CTCLayer': CTCLayer})
            captcha_length = 5

            with open('trained_models/captcha_type_a.pickle', 'rb') as file:
                characters = pickle.load(file)

            return trained_model, characters, captcha_length
        elif captcha_type == 1:
            trained_model = load_model('trained_models/captcha_type_b.h5', custom_objects={'CTCLayer': CTCLayer})
            captcha_length = 6

            with open('trained_models/captcha_type_b.pickle', 'rb') as file:
                characters = pickle.load(file)

            return trained_model, characters, captcha_length

    @staticmethod
    async def add_captcha_solve_query(user_id, captcha_type, image_metadata, prediction_text):
        user_db = ModelCaptchaSolveQuery(captcha_metadata=image_metadata,
                                         captcha_type=captcha_type,
                                         captcha_solution=prediction_text,
                                         user_id=user_id)
        db.session.add(user_db)
        db.session.commit()

    @staticmethod
    async def reduce_user_credit_balance(user_id):
        current_credit_balance = db.session.query(ModelUser).filter(ModelUser.id == user_id).first()

        if current_credit_balance.credit_balance > 1:
            db.session.query(ModelUser).filter(ModelUser.id == user_id)\
                .update({ModelUser.credit_balance: ModelUser.credit_balance - 1})

            db.session.commit()
