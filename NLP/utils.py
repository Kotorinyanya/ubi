import xlrd
from tensorflow.python.client import device_lib
import numpy as np


def to_normal(data):
    '''
    calculate weight by vote_up_count, vote_funny_count, comment_count
    :param data: data dictionary list
    :return: data dictionary list
    '''
    weight_vote_up = 1.0
    weight_vote_funny = 0.5
    weight_comment = 2.0
    max = 0.0
    temp = 0.0
    new_data = list()
    for votes in data:
        if (votes['vote_up_count'] == 0.0 and votes['vote_funny_count'] == 0.0 and votes['comment_count'] == 0.0):
            continue
        votes['weight_temp'] = votes['vote_up_count'] * weight_vote_up + votes['vote_funny_count'] * weight_vote_funny + \
                               votes['comment_count'] * weight_comment
        new_data.append(votes)
        if (max < votes['weight_temp']):
            max = votes['weight_temp']

    zt_list = list()
    zt_gay_list = list()
    for i in range(int(max * 2) + 1):
        zt_list.append(0)
    for votes in new_data:
        zt_list[int(votes['weight_temp'] * 2)] = zt_list[int(votes['weight_temp'] * 2)] + 1
    lenge = len(new_data)
    for i in range(int(max * 2) + 1):
        zt_gay_list.append((temp + zt_list[i] / 2) / lenge)
        temp = temp + zt_list[i]

    for votes in new_data:
        votes['score'] = zt_gay_list[int(votes['weight_temp'] * 2)]
        if (votes['score'] < 0.2):
            votes['class'] = [1, 0, 0, 0]
        elif (votes['score'] < 0.5):
            votes['class'] = [0, 1, 0, 0]
        elif (votes['score'] < 0.8):
            votes['class'] = [0, 0, 1, 0]
        else:
            votes['class'] = [0, 0, 0, 1]
        del votes['vote_up_count']
        del votes['vote_funny_count']
        del votes['comment_count']
        del votes['weight_temp']

    return new_data


# 输入文件路径，返回list;list内包含n个字典形式数据集
def read_xlsx(path):
    '''

    :param path:
    :return:
    '''
    book = xlrd.open_workbook(path)
    first_sheet = book.sheet_by_index(0)
    result = []
    index = 0
    # print(first_sheet.row_values(3))
    key = first_sheet.row_values(index)
    print('key = ', key)
    index += 1
    while (1):
        try:
            # print(type(first_sheet.row_values(index)))
            dic = dict(zip(key, first_sheet.row_values(index)))
            result.append(dic)
            index += 1
        except Exception:
            break
    print('done')
    # print('result = ',result)
    return result, key


def get_available_gpus():
    '''

    :return: number of GPUs
    '''
    local_device_protos = device_lib.list_local_devices()
    return len([x.name for x in local_device_protos if x.device_type == 'GPU'])


# **BUG FIX**
# BUG FIXED: cannot save model while using multi GPU
from keras.layers import Lambda, concatenate
from keras import Model
import tensorflow as tf


def multi_gpu_model(model, gpus):
    '''

    :param model:
    :param gpus:
    :return:
    '''
    if isinstance(gpus, (list, tuple)):
        num_gpus = len(gpus)
        target_gpu_ids = gpus
    else:
        num_gpus = gpus
        target_gpu_ids = range(num_gpus)

    def get_slice(data, i, parts):
        shape = tf.shape(data)
        batch_size = shape[:1]
        input_shape = shape[1:]
        step = batch_size // parts
        if i == num_gpus - 1:
            size = batch_size - step * i
        else:
            size = step
        size = tf.concat([size, input_shape], axis=0)
        stride = tf.concat([step, input_shape * 0], axis=0)
        start = stride * i
        return tf.slice(data, start, size)

    all_outputs = []
    for i in range(len(model.outputs)):
        all_outputs.append([])

    # Place a copy of the model on each GPU,
    # each getting a slice of the inputs.
    for i, gpu_id in enumerate(target_gpu_ids):
        with tf.device('/gpu:%d' % gpu_id):
            with tf.name_scope('replica_%d' % gpu_id):
                inputs = []
                # Retrieve a slice of the input.
                for x in model.inputs:
                    input_shape = tuple(x.get_shape().as_list())[1:]
                    slice_i = Lambda(get_slice,
                                     output_shape=input_shape,
                                     arguments={'i': i,
                                                'parts': num_gpus})(x)
                    inputs.append(slice_i)

                # Apply model on slice
                # (creating a model replica on the target device).
                outputs = model(inputs)
                if not isinstance(outputs, list):
                    outputs = [outputs]

                # Save the outputs for merging back together later.
                for o in range(len(outputs)):
                    all_outputs[o].append(outputs[o])

    # Merge outputs on CPU.
    with tf.device('/cpu:0'):
        merged = []
        for name, outputs in zip(model.output_names, all_outputs):
            merged.append(concatenate(outputs,
                                      axis=0, name=name))
        return Model(model.inputs, merged)


def embedding_model_path(language):
    if language == 'english':
        return 'wiki.en.vec'
    elif language == 'schinese':
        return 'wiki.zh.vec'
    elif language == 'french':
        return 'wiki.fr.vec'
    elif language == 'japanese':
        return 'wiki.ja.vec'
    else:
        return ''


def keras_model_path(language):
    if language == 'english':
        return 'weights.en.h5'
    elif language == 'schinese':
        return 'weights.zh.h5'
    elif language == 'french':
        return 'weights.fr.h5'
    elif language == 'japanese':
        return 'weights.ja.h5'
    else:
        return ''

# build training set
def generate_cart_data(datas, feature_map, output_map):
    n_samples = len(datas)
    n_features = len(feature_map)
    X, Y = np.zeros((n_samples, n_features)), np.zeros((n_samples))
    for i, (data) in enumerate(datas):
        one_sample_X = []
        for feature in feature_map:
            one_sample_X.append(data[feature])
        Y[i] = data[output_map[0]]
        try:
            X[i] = one_sample_X
        except Exception as e:
            print(e)
    X = np.nan_to_num(X)
    Y = np.nan_to_num(Y)

    return X, Y