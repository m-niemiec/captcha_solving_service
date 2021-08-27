import numpy as np
from keras.models import load_model
from keras.preprocessing import image


class RecognizeCaptchaType:
    @staticmethod
    async def get_captcha_type(image_path):
        trained_model = load_model('trained_models/captcha_recognizer_model.h5')

        trained_model.compile(loss='binary_crossentropy',
                              optimizer='adam',
                              metrics=['accuracy'])

        img = image.load_img(image_path, target_size=(32, 32))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)

        images = np.vstack([x])
        classes = trained_model.predict(images, batch_size=10)

        print(int(classes[0][0]))

        return int(classes[0][0])
