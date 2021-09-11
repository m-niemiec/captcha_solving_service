import os
import pickle
import asyncio
import re

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
    # Set semaphore to 5 to prevent server hardware from overloading when analyzing images.
    semaphore = asyncio.Semaphore(5)
    char_to_num = None
    num_to_char = None

    async def get_solution(self, user_id, image_format: str, image_path: str, captcha_type: int, image_metadata: str) -> str:
        async with self.semaphore:
            trained_model, characters, captcha_length = await self.load_proper_model_characters(captcha_type)

            prediction_model = keras.models.Model(
                trained_model.get_layer(name='image').input, trained_model.get_layer(name='dense2').output
            )

            self.char_to_num = layers.experimental.preprocessing.StringLookup(
                vocabulary=characters, mask_token=None
            )

            self.num_to_char = layers.StringLookup(
                vocabulary=self.char_to_num.get_vocabulary(), mask_token=None, invert=True
            )

            image = tf.io.read_file(image_path)

            if image_format == 'jpeg' or image_format == 'jpg':
                image = tf.io.decode_jpeg(image, channels=1)
            elif image_format == 'png':
                image = tf.io.decode_png(image, channels=1)

            image = tf.image.convert_image_dtype(image, tf.float32)
            image = tf.image.resize(image, [50, 200])
            image = tf.transpose(image, perm=[1, 0, 2])

            images = np.expand_dims(image, axis=0)

            prediction = prediction_model.predict(images)
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

                if any(sign in prediction_text for sign in ['=', '+']):
                    try:
                        prediction_text = re.findall(r'([0-9\+\-\\\*]+)', prediction_text)[0]
                        prediction_text = str(eval(prediction_text))
                    except (IndexError, SyntaxError):
                        pass

                return prediction_text

    def decode_batch_predictions(self, pred, captcha_length):
        input_len = np.ones(pred.shape[0]) * pred.shape[1]
        results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :captcha_length]
        # Iterate over the results and get back the text
        output_text = []
        for res in results:
            res = tf.strings.reduce_join(self.num_to_char(res)).numpy().decode('utf-8')
            output_text.append(res)

        return output_text

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
        user = db.session.query(ModelUser).filter(ModelUser.id == user_id).first()
        user.credit_balance -= 1

        db.session.commit()
