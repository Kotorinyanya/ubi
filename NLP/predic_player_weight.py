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
    data = [{'group_count': 69.0, 'dlc_count': 0.0, 'friend_count': 433.0, 'recommendationid': 77400.0, 'screenshot_count': 1735.0, 'steam_weight': 0.534743, 'registered_at': 1064192880.0, 'steamid': 7.65611979612211e+16, 'level': 58.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 247.0, 'badge_count': 110.0, 'review_count': 8.0}, {'group_count': 16.0, 'dlc_count': 520.0, 'friend_count': 154.0, 'recommendationid': 82768.0, 'screenshot_count': 72.0, 'steam_weight': 0.47619, 'registered_at': 1064395113.0, 'steamid': 7.65611979613316e+16, 'level': 26.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 1041.0, 'badge_count': 23.0, 'review_count': 13.0}, {'group_count': 7.0, 'dlc_count': 239.0, 'friend_count': 48.0, 'recommendationid': 135312.0, 'screenshot_count': 259.0, 'steam_weight': 0.47619, 'registered_at': 1069601708.0, 'steamid': 7.65611979629717e+16, 'level': 45.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 318.0, 'badge_count': 112.0, 'review_count': 96.0}, {'group_count': 8.0, 'dlc_count': 0.0, 'friend_count': 103.0, 'recommendationid': 291246.0, 'screenshot_count': 840.0, 'steam_weight': 0.489392, 'registered_at': 1091098992.0, 'steamid': 7.656119796778042e+16, 'level': 27.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 496.0, 'badge_count': 27.0, 'review_count': 5.0}, {'group_count': 0.0, 'dlc_count': 0.0, 'friend_count': 0.0, 'recommendationid': 365781.0, 'screenshot_count': 0.0, 'steam_weight': 0.462636, 'registered_at': 0.0, 'steamid': 7.656119796971475e+16, 'level': 0.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 307.0, 'badge_count': 0.0, 'review_count': 26.0}, {'group_count': 6.0, 'dlc_count': 0.0, 'friend_count': 170.0, 'recommendationid': 388709.0, 'screenshot_count': 81.0, 'steam_weight': 0.510999, 'registered_at': 1100391990.0, 'steamid': 7.65611979702862e+16, 'level': 52.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 947.0, 'badge_count': 100.0, 'review_count': 138.0}, {'group_count': 1.0, 'dlc_count': 534.0, 'friend_count': 59.0, 'recommendationid': 414200.0, 'screenshot_count': 117.0, 'steam_weight': 0.443097, 'registered_at': 1100650698.0, 'steamid': 7.656119797048029e+16, 'level': 34.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 656.0, 'badge_count': 48.0, 'review_count': 46.0}, {'group_count': 87.0, 'dlc_count': 0.0, 'friend_count': 109.0, 'recommendationid': 569857.0, 'screenshot_count': 174.0, 'steam_weight': 0.47619, 'registered_at': 1103992710.0, 'steamid': 7.65611979723172e+16, 'level': 40.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 422.0, 'badge_count': 45.0, 'review_count': 3.0}, {'group_count': 13.0, 'dlc_count': 0.0, 'friend_count': 95.0, 'recommendationid': 741140.0, 'screenshot_count': 241.0, 'steam_weight': 0.467146, 'registered_at': 1121926643.0, 'steamid': 7.656119797708189e+16, 'level': 15.0, 'appid': 12120.0, 'workshop_item_count': 8.0, 'game_count': 533.0, 'badge_count': 6.0, 'review_count': 368.0}, {'group_count': 12.0, 'dlc_count': 458.0, 'friend_count': 116.0, 'recommendationid': 754493.0, 'screenshot_count': 59.0, 'steam_weight': 0.50096, 'registered_at': 1123723704.0, 'steamid': 7.656119797745182e+16, 'level': 41.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 415.0, 'badge_count': 48.0, 'review_count': 39.0}, {'group_count': 31.0, 'dlc_count': 0.0, 'friend_count': 447.0, 'recommendationid': 791320.0, 'screenshot_count': 254.0, 'steam_weight': 0.51795, 'registered_at': 1128379746.0, 'steamid': 7.656119797845651e+16, 'level': 30.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 274.0, 'badge_count': 30.0, 'review_count': 4.0}, {'group_count': 17.0, 'dlc_count': 0.0, 'friend_count': 83.0, 'recommendationid': 798019.0, 'screenshot_count': 331.0, 'steam_weight': 0.487805, 'registered_at': 1129335357.0, 'steamid': 7.656119797865584e+16, 'level': 12.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 140.0, 'badge_count': 7.0, 'review_count': 35.0}, {'group_count': 47.0, 'dlc_count': 810.0, 'friend_count': 248.0, 'recommendationid': 808582.0, 'screenshot_count': 139.0, 'steam_weight': 0.53472, 'registered_at': 1130958770.0, 'steamid': 7.656119797899736e+16, 'level': 73.0, 'appid': 12120.0, 'workshop_item_count': 2.0, 'game_count': 988.0, 'badge_count': 120.0, 'review_count': 39.0}, {'group_count': 9.0, 'dlc_count': 229.0, 'friend_count': 71.0, 'recommendationid': 816171.0, 'screenshot_count': 23.0, 'steam_weight': 0.502488, 'registered_at': 1132193493.0, 'steamid': 7.656119797922893e+16, 'level': 20.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 248.0, 'badge_count': 18.0, 'review_count': 50.0}, {'group_count': 10.0, 'dlc_count': 203.0, 'friend_count': 63.0, 'recommendationid': 857513.0, 'screenshot_count': 925.0, 'steam_weight': 0.518519, 'registered_at': 1136580099.0, 'steamid': 7.656119798024976e+16, 'level': 46.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 187.0, 'badge_count': 108.0, 'review_count': 24.0}, {'group_count': 14.0, 'dlc_count': 0.0, 'friend_count': 163.0, 'recommendationid': 915523.0, 'screenshot_count': 752.0, 'steam_weight': 0.52381, 'registered_at': 1144175558.0, 'steamid': 7.656119798191693e+16, 'level': 12.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 223.0, 'badge_count': 6.0, 'review_count': 65.0}, {'group_count': 89.0, 'dlc_count': 0.0, 'friend_count': 317.0, 'recommendationid': 941898.0, 'screenshot_count': 2485.0, 'steam_weight': 0.470581, 'registered_at': 1147808123.0, 'steamid': 7.656119798265334e+16, 'level': 35.0, 'appid': 12120.0, 'workshop_item_count': 11.0, 'game_count': 215.0, 'badge_count': 23.0, 'review_count': 12.0}, {'group_count': 18.0, 'dlc_count': 608.0, 'friend_count': 189.0, 'recommendationid': 959065.0, 'screenshot_count': 314.0, 'steam_weight': 0.517767, 'registered_at': 1149814470.0, 'steamid': 7.656119798306214e+16, 'level': 107.0, 'appid': 12120.0, 'workshop_item_count': 9.0, 'game_count': 781.0, 'badge_count': 241.0, 'review_count': 72.0}, {'group_count': 3.0, 'dlc_count': 446.0, 'friend_count': 59.0, 'recommendationid': 959601.0, 'screenshot_count': 2078.0, 'steam_weight': 0.504951, 'registered_at': 1150046766.0, 'steamid': 7.65611979830754e+16, 'level': 44.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 502.0, 'badge_count': 59.0, 'review_count': 37.0}, {'group_count': 75.0, 'dlc_count': 0.0, 'friend_count': 412.0, 'recommendationid': 1250394.0, 'screenshot_count': 2925.0, 'steam_weight': 0.494336, 'registered_at': 1180197558.0, 'steamid': 7.656119799008763e+16, 'level': 54.0, 'appid': 12120.0, 'workshop_item_count': 26.0, 'game_count': 4378.0, 'badge_count': 81.0, 'review_count': 188.0}]
    p = PPW(data)
    print(p.result)