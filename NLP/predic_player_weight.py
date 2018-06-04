import matplotlib.pyplot as plt
import json
from utils import read_xlsx, generate_cart_data
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import BaggingRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import RandomForestRegressor
import pickle
from sklearn.externals import joblib


class PPW:
    # Predict Player Weight
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.model_file = './models/CART.pkl'
        self.estimator = joblib.load(self.model_file)

        self.feature_map = ['level', 'review_count', 'screenshot_count', 'workshop_item_count', 'badge_count',
                            'group_count',
                            'game_count', 'dlc_count', 'friend_count']
        self.output_map = ['steam_weight']

        self.result = self.predict(self.data_dict)

    def predict(self, data_dict):
        X, _ = generate_cart_data(data_dict, self.feature_map, self.output_map)
        y_predict = self.estimator.predict(X)
        return y_predict


if __name__ == '__main__':
    data = [{'group_count': 69.0, 'dlc_count': 0.0, 'friend_count': 433.0, 'recommendationid': 77400.0,
             'screenshot_count': 1735.0, 'steam_weight': 0.534743, 'registered_at': 1064192880.0,
             'steamid': 7.65611979612211e+16, 'level': 58.0, 'appid': 12120.0, 'workshop_item_count': 0.0,
             'game_count': 247.0, 'badge_count': 110.0, 'review_count': 8.0},
            {'group_count': 16.0, 'dlc_count': 520.0, 'friend_count': 154.0, 'recommendationid': 82768.0,
             'screenshot_count': 72.0, 'steam_weight': 0.47619, 'registered_at': 1064395113.0,
             'steamid': 7.65611979613316e+16, 'level': 26.0, 'appid': 12120.0, 'workshop_item_count': 1.0,
             'game_count': 1041.0, 'badge_count': 23.0, 'review_count': 13.0},
            {'group_count': 7.0, 'dlc_count': 239.0, 'friend_count': 48.0, 'recommendationid': 135312.0,
             'screenshot_count': 259.0, 'steam_weight': 0.47619, 'registered_at': 1069601708.0,
             'steamid': 7.65611979629717e+16, 'level': 45.0, 'appid': 12120.0, 'workshop_item_count': 1.0,
             'game_count': 318.0, 'badge_count': 112.0, 'review_count': 96.0}]
    p = PPW(data)
    print(p.result)
