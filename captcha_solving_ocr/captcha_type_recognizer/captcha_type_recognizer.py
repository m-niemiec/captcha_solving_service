from pathlib import Path

from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from keras.models import Sequential
from keras.preprocessing.image import ImageDataGenerator
from twiggy import quick_setup, log

quick_setup()  # Set basic logging functions from Twiggy

FILTER_SIZE = 3
NUM_FILTERS = 32
INPUT_SIZE = 32
MAXPOOL_SIZE = 2
BATCH_SIZE = 16
STEPS_PER_EPOCH = 16 // BATCH_SIZE
EPOCHS = 50


def train_recognizer_model():
    """
    Most of this code comes from book "Neural Network Projects with Python" written by James Loy.
    I did only some minor changes.
    """

    model = Sequential()

    model.add(Conv2D(NUM_FILTERS, (FILTER_SIZE, FILTER_SIZE), input_shape=(INPUT_SIZE, INPUT_SIZE, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(MAXPOOL_SIZE, MAXPOOL_SIZE)))
    model.add(Conv2D(NUM_FILTERS, (FILTER_SIZE, FILTER_SIZE), activation='relu'))
    model.add(MaxPooling2D(pool_size=(MAXPOOL_SIZE, MAXPOOL_SIZE)))
    model.add(Flatten())
    model.add(Dense(units=128, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(units=1, activation='sigmoid'))

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    training_src: Path = Path('captcha_type_recognizer/captcha_data_train_sets/train')
    testing_src: Path = Path('captcha_type_recognizer/captcha_data_train_sets/test')

    training_data_generator = ImageDataGenerator()
    testing_data_generator = ImageDataGenerator()

    training_set = training_data_generator.flow_from_directory(training_src,
                                                               target_size=(INPUT_SIZE, INPUT_SIZE),
                                                               batch_size=BATCH_SIZE,
                                                               class_mode='binary')

    test_set = testing_data_generator.flow_from_directory(testing_src,
                                                          target_size=(INPUT_SIZE, INPUT_SIZE),
                                                          batch_size=BATCH_SIZE,
                                                          class_mode='binary')

    model.fit(training_set, steps_per_epoch=STEPS_PER_EPOCH, epochs=EPOCHS, verbose=1)

    score = model.evaluate_generator(test_set, steps=100)

    for idx, metric in enumerate(model.metrics_names):
        log.info(f' {"-" * 10} {metric}: {score[idx]} {"-" * 10} ')

    model.save('captcha_recognizer_model.h5')
    log.info(f' {"-" * 10} Captcha Type Recognizer model saved as captcha_recognizer_model.h5 {"-" * 10} ')
