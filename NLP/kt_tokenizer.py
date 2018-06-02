from keras.preprocessing import sequence
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from keras.preprocessing.text import Tokenizer
import tqdm
import jieba
from cltk.tokenize.word import WordTokenizer
import tinysegmenter


def english_tokenizer(docs, MAX_NB_WORDS, max_seq_len):
    # set stop words
    tokenizer = RegexpTokenizer(r'\w+')
    stop_words = set(stopwords.words('english'))
    stop_words.update(['.', ',', '"', "'", ':', ';', '(', ')', '[', ']', '{', '}'])

    # pre-processing train data
    print("pre-processing train data...")
    processed_docs = []
    for doc in docs:
        tokens = tokenizer.tokenize(doc)
        filtered = [word for word in tokens if word not in stop_words]
        processed_docs.append(" ".join(filtered))

    # tokenizing input data
    print("tokenizing input data...")
    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, lower=True, char_level=False)
    tokenizer.fit_on_texts(processed_docs)  # leaky
    word_seq = tokenizer.texts_to_sequences(processed_docs)
    word_index = tokenizer.word_index
    print("dictionary size: ", len(word_index))

    word_seq = sequence.pad_sequences(word_seq, maxlen=max_seq_len)

    return word_seq, word_index


def chinese_tokenizer(docs, MAX_NB_WORDS, max_seq_len):
    # tokenizing input data
    print("tokenizing input data...")
    tokens = []
    for doc in docs:
        tokens.append(list(jieba.cut(doc)))

    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, lower=False)
    tokenizer.fit_on_texts(tokens)
    word_seq = tokenizer.texts_to_sequences(tokens)
    word_index = tokenizer.word_index
    print("dictionary size: ", len(word_index))

    word_seq = sequence.pad_sequences(word_seq, maxlen=max_seq_len)

    return word_seq, word_index


def french_tokenizer(docs, MAX_NB_WORDS, max_seq_len):
    # tokenizing input data
    word_tokenizer = WordTokenizer('french')
    tokens = []
    for doc in docs:
        tokens.append(word_tokenizer.tokenize(doc))

    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, lower=False)
    tokenizer.fit_on_texts(tokens)
    word_seq = tokenizer.texts_to_sequences(tokens)
    word_index = tokenizer.word_index
    print("dictionary size: ", len(word_index))

    word_seq = sequence.pad_sequences(word_seq, maxlen=max_seq_len)

    return word_seq, word_index


def japanese_tokenizer(docs, MAX_NB_WORDS, max_seq_len):
    # tokenizing input data
    tokens = []
    for doc in docs:
        tokens.append(tinysegmenter.tokenize(doc))

    tokenizer = Tokenizer(num_words=MAX_NB_WORDS, lower=False)
    tokenizer.fit_on_texts(tokens)
    word_seq = tokenizer.texts_to_sequences(tokens)
    word_index = tokenizer.word_index
    print("dictionary size: ", len(word_index))

    word_seq = sequence.pad_sequences(word_seq, maxlen=max_seq_len)

    return word_seq, word_index


def kt_tokenizer(docs, language, MAX_NB_WORDS, max_seq_len):
    '''

    :param docs: text
    :param language:
    :param max_len: max length of tokens
    :return: tokens
    '''
    if language == 'english':
        tokens = english_tokenizer(docs, MAX_NB_WORDS, max_seq_len)
    elif language == 'schinese':
        tokens = chinese_tokenizer(docs, MAX_NB_WORDS, max_seq_len)
    elif language == 'french':
        tokens = french_tokenizer(docs, MAX_NB_WORDS, max_seq_len)
    elif language == 'japanese':
        tokens = japanese_tokenizer(docs, MAX_NB_WORDS, max_seq_len)
    else:
        raise Exception("This language is not yes supported: {0}".format(language))

    return tokens
