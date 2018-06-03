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
from sklearn import tree

# load data
file_path = './data/reviews_users_weight_stripped.xlsx'
datas, keys = read_xlsx(file_path)

keys = ['recommendationid', 'appid', 'steamid', 'steam_weight', 'level', 'review_count', 'screenshot_count',
        'workshop_item_count', 'badge_count', 'group_count', 'game_count', 'dlc_count', 'friend_count', 'registered_at']

feature_map = ['level', 'review_count', 'screenshot_count', 'workshop_item_count', 'badge_count', 'group_count',
               'game_count', 'dlc_count', 'friend_count']
output_map = ['steam_weight']

n_features = len(feature_map)
n_output = len(output_map)
n_data = len(datas)

n_repeat = 20  # Number of iterations for computing expectations
noise = 0.1  # Standard deviation of the noise

print(n_data)

split_percent = 0.6  # percentage of the training data
train_data = datas[:int(split_percent * n_data)]
validation_data = datas[int(split_percent * n_data):]

n_train = len(train_data)
n_validation = len(validation_data)


train_X, train_Y = generate_cart_data(train_data, feature_map, output_map)
validation_X, validation_Y = generate_cart_data(validation_data, feature_map, output_map)

# train
# estimator = BaggingRegressor()
# estimator = RandomForestRegressor(n_estimators=1000)
estimator = DecisionTreeRegressor()
estimator.fit(train_X, train_Y)
y_predict = estimator.predict(validation_X)
estimator.score(validation_X, validation_Y)

plt.plot(estimator.predict(train_X), 'r', label='Y_predict')
plt.plot(train_Y, 'b', label='Y_train')
plt.legend()
plt.show()

plt.plot(y_predict, 'r', label='Y_Predict')
plt.plot(validation_Y, 'b', label='Y_Validation')
plt.legend()
plt.show()

joblib.dump(estimator, './models/CART.pkl')
tree.export_graphviz(estimator, 'tree.dot')