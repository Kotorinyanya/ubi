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
```
```
Using TensorFlow backend.
[0.55119322 0.48515415 0.46089013]
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