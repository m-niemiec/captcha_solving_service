import logging

from tensorflow import keras


class TrainModel:
    def __init__(self, prepare_data):
        self.prepare_data = prepare_data
        self.prediction_model = None

    def train_model(self, model):
        epochs = 300
        early_stopping_patience = 50
        # Add early stopping
        early_stopping = keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=early_stopping_patience, restore_best_weights=True
        )

        # Train the model
        model.fit(
            self.prepare_data.train_dataset,
            validation_data=self.prepare_data.validation_dataset,
            epochs=epochs,
            callbacks=[early_stopping],
        )

        # Get the prediction model by extracting layers till the output layer
        self.prediction_model = keras.models.Model(
            model.get_layer(name="image").input, model.get_layer(name="dense2").output
        )
        self.prediction_model.summary()

        # Save model
        logging.info("Saving model ...")
        model.save(f"{self.prepare_data.captcha_set_to_train}.h5")
        logging.info(f"Model saved under name - {self.prepare_data.captcha_set_to_train}.h5")

        return self.prediction_model
