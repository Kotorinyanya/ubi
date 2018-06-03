import paralleldots
import json
import os


class NLPMH:
    # NLP Main Handler
    def __init__(self, data_dict, api_key, num_reviews=10):
        self.data_dict = data_dict
        self.language = data_dict[0]['language']
        # sort data by weight
        self.sorted_data_dict = self.sort_reviews_by_weight(self.data_dict)

        try:
            # self.api_key = os.environ.get('API_KEY')
            # print(self.api_key)
            self.api_key = api_key
        except Exception as e:
            raise Exception("please add your Paralleldots API_KEY to your environment variable")

        paralleldots.set_api_key(self.api_key)

        self.text = self.piece_text(self.sorted_data_dict)

        self.go(self.text, self.language, num_reviews)

        self.result = dict()
        self.result['keywords'] = self.key_words
        self.result['phrase'] = self.key_phrase
        self.result['emotion'] = self.emotion

    def go(self, text, language):
        if self.language == 'english':
            self.key_words = paralleldots.keywords(text)
            self.key_phrase = paralleldots.phrase_extractor(text)
            self.emotion = paralleldots.emotion(text)
        elif self.language == 'schinese':
            self.key_words = {
                'Error': 'The lang_code is not among the supported languages, supported languages: en, pt, zh, es, de, fr, nl, it, ja, th, da, fi, el, ru, ar.',
                'code': 400}  # API not yet available
            self.key_phrase = paralleldots.multilang_keywords(text, 'zh')
            self.emotion = paralleldots.emotion(text, 'zh')
        elif self.language == 'french':
            self.key_words = paralleldots.multilang_keywords(text, 'fr')
            self.key_phrase = paralleldots.multilang_keywords(text, 'fr')
            self.emotion = paralleldots.emotion(text, 'fr')
        elif self.language == 'japanese':
            self.key_words = paralleldots.multilang_keywords(text, 'ja')
            self.key_phrase = paralleldots.multilang_keywords(text, 'ja')
            self.emotion = paralleldots.emotion(text, 'ja')
        else:
            self.key_words, self.key_phrase, self.emotion = [], [], []

    def sort_reviews_by_weight(self, data_dict):
        weighted_data_dict = []
        for data in data_dict:
            weight = data['review_weight'] * 2 + data['user_weight']
            data['weight'] = weight
            weighted_data_dict.append(data)

        sorted_data_dict = sorted(weighted_data_dict, key=lambda k: k['weight'])
        return sorted_data_dict

    def piece_text(self, data_dict, num_reviews):
        data_dict = data_dict[:num_reviews]
        text = ''
        for i in range(0, len(data_dict)):
            # if i <= len(data_dict) * 0.1:
            #     text += data_dict[i]['content'] + '\n'
            #     text += data_dict[i]['content'] + '\n'
            #     text += data_dict[i]['content'] + '\n'
            # elif i <= len(data_dict) * 0.2:
            #     text += data_dict[i]['content'] + '\n'
            #     text += data_dict[i]['content'] + '\n'
            # else:
            text += data_dict[i]['content'] + '\n'

        return text


if __name__ == '__main__':
    data = [{'content': '嘤嘤嘤，我是小可爱', 'language': 'schinese', 'review_weight': 0.7, 'user_weight': 0.8}]
    f = open("out")
    d = json.loads(f.read())
    n = NLPMH(
        d["positive"]["359550"]["15"]["2018-05-30"]["english"],
        api_key='bSrmexJKMkkSQZIPmAUwRfh7ypzR0c6Gn9jhBegopu0'
    )
    # n = NLPMH(data, api_key='bSrmexJKMkkSQZIPmAUwRfh7ypzR0c6Gn9jhBegopu0')
    print(n.result)
