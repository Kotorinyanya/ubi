import paralleldots
import os


class NLPMH:
    # NLP Main Handler
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.language = data_dict[0]['language']
        # sort data by weight
        self.sorted_data_dict = self.sort_reviews_by_weight(self.data_dict)

        try:
            self.api_key = os.environ.get('API_KEY')
        except Exception as e:
            raise Exception("please add your Paralleldots API_KEY to your environment variable")


        paralleldots.set_api_key(self.api_key)

        self.text = self.piece_text(self.sorted_data_dict)

        self.go(self.text, self.language)

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
            self.key_words = []  # API not yet available
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

    def get_keywords(self, data_dict):

    def piece_text(self, data_dict):
        data_dict = data_dict[:100]
        text = ''
        for i in range(0, len(data_dict)):
            if i <= len(data_dict) * 0.1:
                text += data_dict[i] + '\n'
                text += data_dict[i] + '\n'
                text += data_dict[i] + '\n'
            elif i <= len(data_dict) * 0.2:
                text += data_dict[i] + '\n'
                text += data_dict[i] + '\n'
            else:
                text += data_dict[i] + '\n'

        return text


if __name__ == '__main__':
    data = []
    n = NLPMH(data)
    print(n.result)
