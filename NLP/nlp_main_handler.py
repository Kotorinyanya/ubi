import paralleldots
import json
import os
import re


class NLPMH:
    # NLP Main Handler
    def __init__(self, data_dict, api_key, num_reviews=10):
        self.data_dict = data_dict
        self.language = data_dict[0]['language']
        # sort data by weight
        self.sorted_data_dict = self.sort_reviews_by_weight(self.data_dict)

        # try:
        #     self.api_key = os.environ.get('API_KEY')
        #     print(self.api_key)
        # except Exception as e:
        #     raise Exception("please add your Paralleldots API_KEY to your environment variable")

        self.api_key = api_key

        paralleldots.set_api_key(self.api_key)

        self.text = self.piece_text(self.sorted_data_dict, num_reviews)
        self.text = self.strip_text(self.text, self.language)

        self.key_words, self.key_phrase, self.emotion = self.go(self.text, self.language)

        self.result = dict()
        self.result['keywords'] = self.key_words
        self.result['phrase'] = self.key_phrase
        self.result['emotion'] = self.emotion

    def strip_text(self, text, language):
        '''
        For the reason that Paralledots API only support single language at one call,
        chinese characters inside a English API call must be striped.
        :param text:
        :param language:
        :return:
        '''
        if language == 'english':
            return ''.join([i if ord(i) < 128 else ' ' for i in text])
        else:
            # TODO: strip other language characters
            return text

    def go(self, text, language):
        if language == 'english':
            key_words = paralleldots.keywords(text)
            key_phrase = paralleldots.phrase_extractor(text)
            emotion = paralleldots.emotion(text)
        elif language == 'schinese':
            key_words = [{
                'Error': 'The lang_code is not among the supported languages, supported languages: en, pt, zh, es, de, fr, nl, it, ja, th, da, fi, el, ru, ar.',
                'code': 400}]  # chinese API not yet available
            key_phrase = paralleldots.multilang_keywords(text, 'zh')
            emotion = paralleldots.emotion(text, 'zh')
        elif language == 'french':
            key_words = paralleldots.multilang_keywords(text, 'fr')
            key_phrase = paralleldots.multilang_keywords(text, 'fr')
            emotion = paralleldots.emotion(text, 'fr')
        elif language == 'japanese':
            key_words = paralleldots.multilang_keywords(text, 'ja')
            key_phrase = paralleldots.multilang_keywords(text, 'ja')
            emotion = paralleldots.emotion(text, 'ja')
        else:
            key_words, key_phrase, emotion = [], [], []

        return key_words, key_phrase, emotion

    def sort_reviews_by_weight(self, data_dict):
        weighted_data_dict = []
        for data in data_dict:
            review_weight, user_weight = 0, 0
            try:
                review_weight = data['review_weight']
                user_weight = data['user_weight']
            except:
                pass
            weight = review_weight + user_weight
            data['weight'] = weight
            weighted_data_dict.append(data)

        sorted_data_dict = sorted(weighted_data_dict, key=lambda k: k['weight'])
        return sorted_data_dict

    def piece_text(self, data_dict, num_reviews):
        data_dict = data_dict[:num_reviews]
        text = ''
        for i in range(0, len(data_dict)):
            if i <= len(data_dict) * 0.1:
                text += data_dict[i]['content'] + '\n'
                text += data_dict[i]['content'] + '\n'
                text += data_dict[i]['content'] + '\n'
            elif i <= len(data_dict) * 0.2:
                text += data_dict[i]['content'] + '\n'
                text += data_dict[i]['content'] + '\n'
            else:
                text += data_dict[i]['content'] + '\n'

        return text


if __name__ == '__main__':
    data1 = [{'content': 'I am cute 嘤嘤嘤', 'language': 'english', 'review_weight': 0.7, 'user_weight': 0.8}]
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
    n = NLPMH(data1, api_key='<api key>')
    print(n.result)
