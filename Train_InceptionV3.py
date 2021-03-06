import pandas
import keras
from keras.callbacks import ModelCheckpoint, EarlyStopping
from keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import TensorBoard
from keras.applications import inception_v3
from keras.optimizers import Adam
from keras.losses import categorical_crossentropy
from datetime import datetime
import tensorflow as tf
import time
import pickle
import os

import telegram
bot = telegram.Bot(token="631334683:AAEKuP9g-WcJ_jJgIvFfaQ99uHs5C5S73nU")

if __name__ == '__main__':

    start = time.time()

    train_datagen = ImageDataGenerator(
        horizontal_flip=True,
        rotation_range=20,
        brightness_range=(0.0,1.0)
    )

    validation_datagen = ImageDataGenerator()

    train_generator = train_datagen.flow_from_directory(
        'Dataset/Training',
        target_size=(200, 300),
        batch_size=25,
        class_mode='categorical',
        color_mode='grayscale'
    )

    validation_generator = validation_datagen.flow_from_directory(
        'Dataset/Validation',
        target_size=(200, 300),
        batch_size=25,
        class_mode='categorical',
        color_mode='grayscale'
    )

    save_dir = os.path.join(os.getcwd(), 'saved_models')
    arch_name = "InceptionV3"
    model_name = 'Model_InceptionV3_' + datetime.now().strftime('%d%m%y') + '.hdf5'
    weight_name = 'Weight_InceptionV3_' + datetime.now().strftime('%d%m%y') + '.hdf5'
    history_name = 'History_InceptionV3_' + datetime.now().strftime('%d%m%y')
    model_path = os.path.join(save_dir, model_name)
    weight_path = os.path.join(save_dir, weight_name)
    EPOCH = 20

    model = inception_v3.InceptionV3(include_top=True, weights=None, classes=70, input_shape=(200, 300, 1))
    # model = load_model(os.getcwd()+'/saved_models/ResNet_checkpoint_050718_14-1.47-0.54.hdf5')
    model.compile(optimizer='adam', loss=categorical_crossentropy, metrics=['acc'])
    model.summary()

    tensorboard = TensorBoard()
    earlystop = EarlyStopping(patience=5)
    checkpoint = ModelCheckpoint(
        filepath=os.path.join(
            save_dir, 'Checkpoint_InceptionV3_' +
            datetime.now().strftime('%d%m%y') +
            '_{epoch:02d}-{val_loss:.2f}-{val_acc:.2f}.hdf5'),
        save_best_only=True,
        verbose=1)

    with tf.Session() as sess :
      sess.run(tf.global_variables_initializer())
      training = model.fit_generator(
          train_generator,
          steps_per_epoch=800,
          epochs=EPOCH,
          validation_data=validation_generator,
          validation_steps=55,
          callbacks=[checkpoint,tensorboard,earlystop],
      )

      score = model.evaluate_generator(
          validation_generator,
          steps=55
      )

    print('\nLoss \t\t:',score[0])
    print('Accuracy \t:',score[1]*100,'%')

    with open(os.path.join(save_dir,history_name), 'wb') as file:
        pickle.dump(training.history, file)

    end = time.time()

    menit = (end-start)/60

    print("\n"+model_name+
          "\n Finished in %.2f minutes"%(menit))

    bot.send_message(chat_id='477030905', text="Training "+arch_name+" finished. "
                        "\nLoss : "+str(score[0])+" Accuracy : "+str(score[1]*100)+"%")