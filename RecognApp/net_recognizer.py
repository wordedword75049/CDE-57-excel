from PIL import Image, ImageDraw
import numpy
import random
import matplotlib.pyplot as plt
import string

import numpy as np

from skimage.transform import resize
from skimage.morphology import label
from sklearn.model_selection import train_test_split

import tensorflow as tf

from keras.models import Model, load_model
from keras.layers import Input, BatchNormalization, Activation, Dense, Dropout
from keras.layers.core import Lambda, RepeatVector, Reshape
from keras.layers.convolutional import Conv2D, Conv2DTranspose
from keras.layers.pooling import MaxPooling2D, GlobalMaxPool2D
from keras.layers.merge import concatenate, add
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img


def generate_images(amount_of_pictures = 1000, image_shape = (512, 512), rect_bottom = 450, betwin = 20, x_first = 40):

    number_weigt_dict = {7: 42, 6: 53, 5:70, 4:90, 8:35}
    
    for i in range(amount_of_pictures):
        img = Image.new("L", image_shape, color="white")
        img_label = Image.new("L", image_shape, color="black")
        columns_amount = random.randint(4, 8)
        rect_up = random.randint(40, 400)
    
        img1 = ImageDraw.Draw(img)
        img1_label = ImageDraw.Draw(img_label)
    
        img1.rectangle([(x_first, rect_up), (x_first+number_weigt_dict[columns_amount], rect_bottom)], fill ="gray")
        img1_label.rectangle([(x_first, rect_up), (x_first+number_weigt_dict[columns_amount], rect_bottom)], fill ="white")
    
        cur_x = x_first+number_weigt_dict[columns_amount]+betwin
    
        for j in range(1, columns_amount):
            rect_up = random.randint(40, 400)
        
            shape = [(cur_x, rect_up), (cur_x+number_weigt_dict[columns_amount], rect_bottom)]
        
            img1.rectangle(shape, fill ="gray")
            img1_label.rectangle(shape, fill ="white")
        
            cur_x = cur_x+number_weigt_dict[columns_amount]+betwin
            
        img1.text((470, 100), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))
        img1.text((470, 150), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))
        img1.text((470, 200), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))
        img1.text((470, 250), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))
        img1.text((470, 300), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))
        img1.text((470, 350), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)))

        img1.text((50, 470), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)))
        img1.text((150, 470), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)))
        img1.text((250, 470), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)))
        img1.text((350, 470), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)))
        img1.text((450, 470), ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(3)))
        
        img.save("images/{}.png".format(i))
        img_label.save("labels/{}.png".format(i))
    
        img.close()
        img_label.close()
    
    
    
def load_model(model_name='model_exp.h5'):
    def conv2d_block(input_tensor, n_filters, kernel_size = 3, batchnorm = True):
        # first layer
        x = Conv2D(filters = n_filters, kernel_size = (kernel_size, kernel_size),\
              kernel_initializer = 'he_normal', padding = 'same')(input_tensor)
        if batchnorm:
            x = BatchNormalization()(x)
        x = Activation('relu')(x)
    
        # second layer
        x = Conv2D(filters = n_filters, kernel_size = (kernel_size, kernel_size),\
                  kernel_initializer = 'he_normal', padding = 'same')(input_tensor)
        if batchnorm:
            x = BatchNormalization()(x)
        x = Activation('relu')(x)
    
        return x
    
    def get_unet(input_img, n_filters = 16, dropout = 0.1, batchnorm = True):
        # Contracting Path
        c1 = conv2d_block(input_img, n_filters * 1, kernel_size = 3, batchnorm = batchnorm)
        p1 = MaxPooling2D((2, 2))(c1)
        p1 = Dropout(dropout)(p1)
    
        c2 = conv2d_block(p1, n_filters * 2, kernel_size = 3, batchnorm = batchnorm)
        p2 = MaxPooling2D((2, 2))(c2)
        p2 = Dropout(dropout)(p2)
    
        c3 = conv2d_block(p2, n_filters * 4, kernel_size = 3, batchnorm = batchnorm)
        p3 = MaxPooling2D((2, 2))(c3)
        p3 = Dropout(dropout)(p3)
    
        c5 = conv2d_block(p3, n_filters = n_filters * 8, kernel_size = 3, batchnorm = batchnorm)
    
        # Expansive Path
    
        u7 = Conv2DTranspose(n_filters * 4, (3, 3), strides = (2, 2), padding = 'same')(c5)
        u7 = concatenate([u7, c3])
        u7 = Dropout(dropout)(u7)
        c7 = conv2d_block(u7, n_filters * 4, kernel_size = 3, batchnorm = batchnorm)
    
        u8 = Conv2DTranspose(n_filters * 2, (3, 3), strides = (2, 2), padding = 'same')(c7)
        u8 = concatenate([u8, c2])
        u8 = Dropout(dropout)(u8)
        c8 = conv2d_block(u8, n_filters * 2, kernel_size = 3, batchnorm = batchnorm)
    
        u9 = Conv2DTranspose(n_filters * 1, (3, 3), strides = (2, 2), padding = 'same')(c8)
        u9 = concatenate([u9, c1])
        u9 = Dropout(dropout)(u9)
        c9 = conv2d_block(u9, n_filters * 1, kernel_size = 3, batchnorm = batchnorm)
    
        outputs = Conv2D(1, (1, 1), activation='sigmoid')(c9)
        model = Model(inputs=[input_img], outputs=[outputs])
        return model
    
    input_img = Input((512, 512, 1), name='img')
    model = get_unet(input_img, n_filters=16, dropout=0.05, batchnorm=True)
    model.compile(optimizer=Adam(), loss="binary_crossentropy", metrics=["accuracy"])
    
    model.load_weights(model_name)
    return model


def get_mask(image_name, image_size=(512, 512, 1)):
    X_graph = []
    img_graph = img_to_array(load_img(image_name, grayscale=True))
    img_graph = resize(img_graph, image_size, mode = 'constant', preserve_range= True)
    img_graph = img_graph/255.0
    X_graph.append(img_graph)
    X_graph = np.array(X_graph)
    
    preds_graph = model.predict(X_graph, verbose=1)
    preds_graph_t = (preds_graph > 0.5).astype(np.uint8)
    
    return preds_graph_t


def plot_result(X, binary_preds, ix=0):
    fig, ax = plt.subplots(1, 2, figsize=(20, 10))
    ax[0].imshow(X[ix, ..., 0], cmap='seismic')
    ax[1].imshow(binary_preds[ix].squeeze(), vmin=0, vmax=1)
    
    
    






