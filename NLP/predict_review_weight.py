from kt_tokenizer import kt_tokenizer
from utils import keras_model_path
from keras.models import load_model


class PRW:
    # Predict Reivew Weight
    def __init__(self, data_dict):
        self.data_dict = data_dict
        self.language = data_dict[0]['language']  # one language at one call

        self.MAX_NB_WORDS = 100000
        self.max_seq_len = 1000

        self.MODEL_DIR = './models/'

        # list of weights
        self.weights = self.predict(self.data_dict, self.language)

    def load_model_by_language(self, language):
        '''
        load model
        :param language:
        :return: model object
        '''
        model_path = self.MODEL_DIR + keras_model_path(language)
        model = load_model(model_path)
        return model

    def predict(self, data_dict, language):
        '''

        :param data_dict: list of dict
        :param language:
        :return: list of weight
        '''
        # load models
        model = self.load_model_by_language(language)

        # pre-process texts
        raw_docs = [data['content'] for data in data_dict]
        word_seq, word_index = kt_tokenizer(raw_docs, language, self.MAX_NB_WORDS, self.max_seq_len)

        # predict
        weight_predicted = model.predict(word_seq)

        return weight_predicted

    def filtering_by_language(self, data_dict, language):
        '''
        filtering other languages
        :param data_dict: list of dict
        :return: list of weights
        '''
        return [data for data in data_dict if data['language'] == language]


if __name__ == '__main__':
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
