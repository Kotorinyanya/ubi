# coding: utf-8

import numpy as np
import pandas as pd
# import seaborn as sns
import matplotlib.pyplot as plt

import keras
from keras import optimizers
from keras import backend as K
from keras import regularizers
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten
from keras.layers import Embedding, Conv1D, MaxPooling1D, GlobalMaxPooling1D, LSTM
from keras.utils import plot_model
from keras.preprocessing import sequence
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping, ModelCheckpoint

from tqdm import tqdm
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
import os, re, csv, math, codecs

from utils import to_normal, read_xlsx, get_available_gpus, embedding_model_path
# from utils import multi_gpu_model
from kt_tokenizer import kt_tokenizer

import tensorflow as tf
from tensorflow.python.client import device_lib


def train(data_dict, emebedding_path, language):
    # pre-process train data
    # data_dict = to_normal(data_dict)

    MAX_NB_WORDS = 100000
    max_seq_len = 1000

    # load train data
    raw_docs_train = [data['content'] for data in data_dict]
    labels = [data['steam_weight'] for data in data_dict]

    word_seq, word_index = kt_tokenizer(raw_docs_train, language, MAX_NB_WORDS, max_seq_len)

    print('{0} reviews in {1}'.format(len(word_seq), language))

    print('loading word embeddings...')
    emebedding_path = EMBEDDING_DIR + embedding_model_path(language)  # TODO
    embeddings_index = {}
    f = codecs.open(emebedding_path, encoding='utf-8')
    for line in f:
        values = line.rstrip().rsplit(' ')
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()
    print('found %s word vectors' % len(embeddings_index))

    y_all = np.array(labels)

    # training params
    batch_size = 256
    num_epochs = 300
    num_gpus = get_available_gpus()

    # model parameters
    num_filters = 64
    embed_dim = 300
    weight_decay = 1e-4
    learning_rate = 0.001

    # output parameters
    num_classes = 4

    # split data
    split_persentage = 0.8
    split_index = int(len(word_seq) * split_persentage)
    word_seq_train = word_seq[:split_index]
    word_seq_test = word_seq[split_index:]
    y_train = y_all[:split_index]
    y_test = y_all[split_index:]

    # embedding matrix
    print('preparing embedding matrix...')
    words_not_found = []
    nb_words = min(MAX_NB_WORDS, len(word_index))
    embedding_matrix = np.zeros((nb_words, embed_dim))
    for word, i in word_index.items():
        if i >= nb_words:
            continue
        embedding_vector = embeddings_index.get(word)
        if (embedding_vector is not None) and len(embedding_vector) > 0:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector
        else:
            words_not_found.append(word)
    print('number of null word embeddings: %d' % np.sum(np.sum(embedding_matrix, axis=1) == 0))
    print("sample words not found: ", np.random.choice(words_not_found, 20))

    # CNN architecture
    print("Defining CNN ...")
    model = Sequential()
    model.add(Embedding(nb_words, embed_dim,
                        weights=[embedding_matrix], input_length=max_seq_len, trainable=False))
    model.add(Conv1D(num_filters, 7, activation='relu', padding='same'))
    model.add(MaxPooling1D(2))
    model.add(Conv1D(num_filters, 7, activation='relu', padding='same'))
    model.add(GlobalMaxPooling1D())
    # model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(32, activation='relu', kernel_regularizer=regularizers.l2(weight_decay)))
    model.add(Dropout(0.5))
    model.add(Dense(16, activation='relu', kernel_regularizer=regularizers.l2(weight_decay)))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))  # multi-label (k-hot encoding)

    adam = optimizers.Adam(lr=learning_rate, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    try:
        model = multi_gpu_model(model, gpus=num_gpus)
        print("Training using {0} GPUs..".format(num_gpus))
    except:
        print("Training using single GPU or CPU..")
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    print(model.summary())

    # save model
    filepath = 'models/' + language + '.' + 'weights.ep{epoch:03d}.loss{loss:.3f}.val_loss{val_loss:.3f}.h5'
    checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=False,
                                 mode='auto', period=1)
    callbacks_list = [checkpoint]

    # model training
    hist = model.fit(word_seq_train, y_train, batch_size=batch_size, epochs=num_epochs, callbacks=callbacks_list,
                     validation_split=0.1, shuffle=True, verbose=2)

    # plot loss
    train_history = hist
    loss = train_history.history['loss']
    val_loss = train_history.history['val_loss']
    plt.title(language + ' ' + 'model')
    plt.plot(loss)
    plt.plot(val_loss)
    plt.legend(['loss', 'val_loss'])
    plt.show()

    # plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)


DATA_PATH = './data/reviews_language_helpful_funny_comment_weight_stripped.xlsx'
EMBEDDING_DIR = '/home/huze/fasttext/'


# read data form xlsx
data_dict, label_name = read_xlsx(DATA_PATH)

# handle different languages
languages = set()
for data in data_dict:
    languages.add(data['language'])
print(languages)


supported_languages = ['english', 'schinese', 'japanese', 'french']
for language in supported_languages:
    current_language_data = [data for data in data_dict if data['language'] == language]
    train(current_language_data, EMBEDDING_DIR, language)