Models for predict review/player weight

Full documentation at https://hackmd.io/lHkWbwjuQciYZehsuc4SxQ?view#NLP-%E5%BA%94%E7%94%A8%E6%8E%A5%E5%8F%A3

### API Examples

#### Predict Review Weight
```python
from predict_review_weight import PRW
data_dict = [
        {
            'content': 'GTA:Hood edition,  With added The Sims\n\nBecause every gangsta knows that they need to keep their hair and clothes looking fresh..',
            'language': 'english'},
        {
            'content': 'IMO, the best GTA. If not just for the voice acting.',
            'language': 'english'},
        {
            'content': 'Gimme a ticket',
            'language': 'english'},
        {
            'content': "Great on PS2, but sadly unplayable on the PC. Controller support is terrible and the interface doesn't work on many resolutions. This game has not aged well.  8/10 on PS2, 0/10 on PC - Do not buy.",
            'language': 'english'}]
r = PRW(data_dict)
print(r.weights)
```
```
Using TensorFlow backend.
2018-06-04 16:26:05.339725: I tensorflow/core/platform/cpu_feature_guard.cc:140] Your CPU supports instructions that this TensorFlow binary was not compiled to use: SSE4.1 SSE4.2 AVX AVX2 FMA
2018-06-04 16:26:11.230402: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 0 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:04:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:11.455621: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 1 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:05:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:11.704523: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 2 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:08:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:11.885706: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 3 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:09:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:12.066588: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 4 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:84:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:12.253722: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 5 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:85:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:12.448813: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 6 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:88:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:12.654816: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1356] Found device 7 with properties:
name: TITAN Xp major: 6 minor: 1 memoryClockRate(GHz): 1.582
pciBusID: 0000:89:00.0
totalMemory: 11.91GiB freeMemory: 11.74GiB
2018-06-04 16:26:12.669245: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1435] Adding visible gpu devices: 0, 1, 2, 3, 4, 5, 6, 7
2018-06-04 16:26:14.847753: I tensorflow/core/common_runtime/gpu/gpu_device.cc:923] Device interconnect StreamExecutor with strength 1 edge matrix:
2018-06-04 16:26:14.847809: I tensorflow/core/common_runtime/gpu/gpu_device.cc:929]      0 1 2 3 4 5 6 7
2018-06-04 16:26:14.847821: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 0:   N Y Y Y N N N N
2018-06-04 16:26:14.847829: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 1:   Y N Y Y N N N N
2018-06-04 16:26:14.847835: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 2:   Y Y N Y N N N N
2018-06-04 16:26:14.847842: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 3:   Y Y Y N N N N N
2018-06-04 16:26:14.847849: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 4:   N N N N N Y Y Y
2018-06-04 16:26:14.847856: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 5:   N N N N Y N Y Y
2018-06-04 16:26:14.847862: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 6:   N N N N Y Y N Y
2018-06-04 16:26:14.847869: I tensorflow/core/common_runtime/gpu/gpu_device.cc:942] 7:   N N N N Y Y Y N
2018-06-04 16:26:14.850158: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:0 with 11370 MB memory) -> physical GPU (device: 0, name: TITAN Xp, pci bus id: 0000:04:00.0, compute capability: 6.1)
2018-06-04 16:26:15.047156: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:1 with 11370 MB memory) -> physical GPU (device: 1, name: TITAN Xp, pci bus id: 0000:05:00.0, compute capability: 6.1)
2018-06-04 16:26:15.273697: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:2 with 11370 MB memory) -> physical GPU (device: 2, name: TITAN Xp, pci bus id: 0000:08:00.0, compute capability: 6.1)
2018-06-04 16:26:15.469338: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:3 with 11370 MB memory) -> physical GPU (device: 3, name: TITAN Xp, pci bus id: 0000:09:00.0, compute capability: 6.1)
2018-06-04 16:26:15.666029: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:4 with 11370 MB memory) -> physical GPU (device: 4, name: TITAN Xp, pci bus id: 0000:84:00.0, compute capability: 6.1)
2018-06-04 16:26:15.849511: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:5 with 11370 MB memory) -> physical GPU (device: 5, name: TITAN Xp, pci bus id: 0000:85:00.0, compute capability: 6.1)
2018-06-04 16:26:16.021748: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:6 with 11370 MB memory) -> physical GPU (device: 6, name: TITAN Xp, pci bus id: 0000:88:00.0, compute capability: 6.1)
2018-06-04 16:26:16.193446: I tensorflow/core/common_runtime/gpu/gpu_device.cc:1053] Created TensorFlow device (/job:localhost/replica:0/task:0/device:GPU:7 with 11370 MB memory) -> physical GPU (device: 7, name: TITAN Xp, pci bus id: 0000:89:00.0, compute capability: 6.1)
pre-processing train data...
tokenizing input data...
dictionary size:  45
[[0.5077709 ]
 [0.5023102 ]
 [0.50469995]
 [0.5070113 ]]
```

#### Predict Player Weight
```python
from predict_player_weight import PPW
data = [{'group_count': 69.0, 'dlc_count': 0.0, 'friend_count': 433.0, 'recommendationid': 77400.0, 'screenshot_count': 1735.0, 'steam_weight': 0.534743, 'registered_at': 1064192880.0, 'steamid': 7.65611979612211e+16, 'level': 58.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 247.0, 'badge_count': 110.0, 'review_count': 8.0}, {'group_count': 16.0, 'dlc_count': 520.0, 'friend_count': 154.0, 'recommendationid': 82768.0, 'screenshot_count': 72.0, 'steam_weight': 0.47619, 'registered_at': 1064395113.0, 'steamid': 7.65611979613316e+16, 'level': 26.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 1041.0, 'badge_count': 23.0, 'review_count': 13.0}, {'group_count': 7.0, 'dlc_count': 239.0, 'friend_count': 48.0, 'recommendationid': 135312.0, 'screenshot_count': 259.0, 'steam_weight': 0.47619, 'registered_at': 1069601708.0, 'steamid': 7.65611979629717e+16, 'level': 45.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 318.0, 'badge_count': 112.0, 'review_count': 96.0}, {'group_count': 8.0, 'dlc_count': 0.0, 'friend_count': 103.0, 'recommendationid': 291246.0, 'screenshot_count': 840.0, 'steam_weight': 0.489392, 'registered_at': 1091098992.0, 'steamid': 7.656119796778042e+16, 'level': 27.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 496.0, 'badge_count': 27.0, 'review_count': 5.0}, {'group_count': 0.0, 'dlc_count': 0.0, 'friend_count': 0.0, 'recommendationid': 365781.0, 'screenshot_count': 0.0, 'steam_weight': 0.462636, 'registered_at': 0.0, 'steamid': 7.656119796971475e+16, 'level': 0.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 307.0, 'badge_count': 0.0, 'review_count': 26.0}, {'group_count': 6.0, 'dlc_count': 0.0, 'friend_count': 170.0, 'recommendationid': 388709.0, 'screenshot_count': 81.0, 'steam_weight': 0.510999, 'registered_at': 1100391990.0, 'steamid': 7.65611979702862e+16, 'level': 52.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 947.0, 'badge_count': 100.0, 'review_count': 138.0}, {'group_count': 1.0, 'dlc_count': 534.0, 'friend_count': 59.0, 'recommendationid': 414200.0, 'screenshot_count': 117.0, 'steam_weight': 0.443097, 'registered_at': 1100650698.0, 'steamid': 7.656119797048029e+16, 'level': 34.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 656.0, 'badge_count': 48.0, 'review_count': 46.0}, {'group_count': 87.0, 'dlc_count': 0.0, 'friend_count': 109.0, 'recommendationid': 569857.0, 'screenshot_count': 174.0, 'steam_weight': 0.47619, 'registered_at': 1103992710.0, 'steamid': 7.65611979723172e+16, 'level': 40.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 422.0, 'badge_count': 45.0, 'review_count': 3.0}, {'group_count': 13.0, 'dlc_count': 0.0, 'friend_count': 95.0, 'recommendationid': 741140.0, 'screenshot_count': 241.0, 'steam_weight': 0.467146, 'registered_at': 1121926643.0, 'steamid': 7.656119797708189e+16, 'level': 15.0, 'appid': 12120.0, 'workshop_item_count': 8.0, 'game_count': 533.0, 'badge_count': 6.0, 'review_count': 368.0}, {'group_count': 12.0, 'dlc_count': 458.0, 'friend_count': 116.0, 'recommendationid': 754493.0, 'screenshot_count': 59.0, 'steam_weight': 0.50096, 'registered_at': 1123723704.0, 'steamid': 7.656119797745182e+16, 'level': 41.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 415.0, 'badge_count': 48.0, 'review_count': 39.0}, {'group_count': 31.0, 'dlc_count': 0.0, 'friend_count': 447.0, 'recommendationid': 791320.0, 'screenshot_count': 254.0, 'steam_weight': 0.51795, 'registered_at': 1128379746.0, 'steamid': 7.656119797845651e+16, 'level': 30.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 274.0, 'badge_count': 30.0, 'review_count': 4.0}, {'group_count': 17.0, 'dlc_count': 0.0, 'friend_count': 83.0, 'recommendationid': 798019.0, 'screenshot_count': 331.0, 'steam_weight': 0.487805, 'registered_at': 1129335357.0, 'steamid': 7.656119797865584e+16, 'level': 12.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 140.0, 'badge_count': 7.0, 'review_count': 35.0}, {'group_count': 47.0, 'dlc_count': 810.0, 'friend_count': 248.0, 'recommendationid': 808582.0, 'screenshot_count': 139.0, 'steam_weight': 0.53472, 'registered_at': 1130958770.0, 'steamid': 7.656119797899736e+16, 'level': 73.0, 'appid': 12120.0, 'workshop_item_count': 2.0, 'game_count': 988.0, 'badge_count': 120.0, 'review_count': 39.0}, {'group_count': 9.0, 'dlc_count': 229.0, 'friend_count': 71.0, 'recommendationid': 816171.0, 'screenshot_count': 23.0, 'steam_weight': 0.502488, 'registered_at': 1132193493.0, 'steamid': 7.656119797922893e+16, 'level': 20.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 248.0, 'badge_count': 18.0, 'review_count': 50.0}, {'group_count': 10.0, 'dlc_count': 203.0, 'friend_count': 63.0, 'recommendationid': 857513.0, 'screenshot_count': 925.0, 'steam_weight': 0.518519, 'registered_at': 1136580099.0, 'steamid': 7.656119798024976e+16, 'level': 46.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 187.0, 'badge_count': 108.0, 'review_count': 24.0}, {'group_count': 14.0, 'dlc_count': 0.0, 'friend_count': 163.0, 'recommendationid': 915523.0, 'screenshot_count': 752.0, 'steam_weight': 0.52381, 'registered_at': 1144175558.0, 'steamid': 7.656119798191693e+16, 'level': 12.0, 'appid': 12120.0, 'workshop_item_count': 1.0, 'game_count': 223.0, 'badge_count': 6.0, 'review_count': 65.0}, {'group_count': 89.0, 'dlc_count': 0.0, 'friend_count': 317.0, 'recommendationid': 941898.0, 'screenshot_count': 2485.0, 'steam_weight': 0.470581, 'registered_at': 1147808123.0, 'steamid': 7.656119798265334e+16, 'level': 35.0, 'appid': 12120.0, 'workshop_item_count': 11.0, 'game_count': 215.0, 'badge_count': 23.0, 'review_count': 12.0}, {'group_count': 18.0, 'dlc_count': 608.0, 'friend_count': 189.0, 'recommendationid': 959065.0, 'screenshot_count': 314.0, 'steam_weight': 0.517767, 'registered_at': 1149814470.0, 'steamid': 7.656119798306214e+16, 'level': 107.0, 'appid': 12120.0, 'workshop_item_count': 9.0, 'game_count': 781.0, 'badge_count': 241.0, 'review_count': 72.0}, {'group_count': 3.0, 'dlc_count': 446.0, 'friend_count': 59.0, 'recommendationid': 959601.0, 'screenshot_count': 2078.0, 'steam_weight': 0.504951, 'registered_at': 1150046766.0, 'steamid': 7.65611979830754e+16, 'level': 44.0, 'appid': 12120.0, 'workshop_item_count': 0.0, 'game_count': 502.0, 'badge_count': 59.0, 'review_count': 37.0}, {'group_count': 75.0, 'dlc_count': 0.0, 'friend_count': 412.0, 'recommendationid': 1250394.0, 'screenshot_count': 2925.0, 'steam_weight': 0.494336, 'registered_at': 1180197558.0, 'steamid': 7.656119799008763e+16, 'level': 54.0, 'appid': 12120.0, 'workshop_item_count': 26.0, 'game_count': 4378.0, 'badge_count': 81.0, 'review_count': 188.0}]
p = PPW(data)
print(p.result)
```
```
Using TensorFlow backend.
[0.55119322 0.48515415 0.46089013 0.5328038  0.4777544  0.5647041
 0.4706884  0.52052058 0.4628447  0.49937495 0.5050101  0.47834817
 0.51889363 0.48449537 0.51959465 0.5083242  0.4778817  0.5578019
 0.50341258 0.5089834 ]
```

#### Get keywords / phrase / emotion
```python
data1 = [{'content': 'I am cute', 'language': 'english', 'review_weight': 0.7, 'user_weight': 0.8}]
data2 = [{'content': '私は可愛いです', 'language': 'japanese', 'review_weight': 0.5}]
data3 = [{'content': '嘤嘤嘤，我是小可爱', 'language': 'schinese', 'review_weight': 0.5, 'user_weight': 0.7}]
data4 = [{'content': 'Je suis un peu mignon', 'language': 'french', 'review_weight': 0.5, 'user_weight': 0.7}]
# f = open("out")
# d = json.loads(f.read())
# n = NLPMH(
#     d["positive"]["359550"]["15"]["2018-05-30"]["english"],
#     api_key='<api key>',
#     num_reviews=1
# )
n = NLPMH(data4, api_key='<api key>')
print(n.result)
```
```
{'keywords': {'keywords': [{'confidence_score': 1.0, 'keyword': 'mignon'}], 'code': 200}, 'phrase': {'keywords': [{'confidence_score': 1.0, 'keyword': 'mignon'}], 'code': 200}, 'emotion': {'code': 200, 'emotion': {'probabilities': {'Sarcasm': 0.195980936686959, 'Angry': 0.014860588835207649, 'Excited': 0.2716989084979747, 'Bored': 0.014332206487795216, 'Fear': 0.04142715446654994, 'Sad': 0.026047452507366828, 'Happy': 0.43565275251814684}, 'emotion': 'Happy'}}}
```