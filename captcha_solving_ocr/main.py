from pathlib import Path

from build_model import BuildModel
from check_model_accuracy import CheckModelAccuracy
from prepare_data import PrepareData
from train_model import TrainModel

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

    # Show training data set
    PrepareData(*arguments).show_train_data_set()

    # Get model
    model = BuildModel(*arguments).build_model()
    model.summary()

    # Train Model
    trained_model = TrainModel(*arguments).train_model(model)

    # Show Model Accuracy
    CheckModelAccuracy(*arguments).show_validation_dataset(trained_model)


if __name__ == '__main__':
    main()
