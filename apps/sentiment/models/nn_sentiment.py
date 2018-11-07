### adapted from https://www.kaggle.com/ngyptr/lstm-sentiment-analysis-keras


import numpy as np
import pandas as pd
import logging

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
import re
import pickle
from keras.models import load_model

DEFAULT_MODEL_FILENAME = 'lstm_model.h5'
DEFAULT_TOKENIZER_FILENAME = 'tokenizer.pkl'

def train_model(model_path=DEFAULT_MODEL_FILENAME, tokenizer_path=DEFAULT_TOKENIZER_FILENAME,
                csv_path = 'sentiment-analysis_dataset.csv', validate=False):

    data = pd.read_csv(csv_path, error_bad_lines=False)
    data = data[['text', 'sentiment']]

    data['text'] = data['text'].apply(lambda x: x.lower())
    data['text'] = data['text'].apply((lambda x: re.sub('[^a-zA-z0-9\s]', '', x)))

    logging.info('Positive training examples: ' + data[data['sentiment'] == 1].size)
    logging.info('Negative training examples: ' + data[data['sentiment'] == 0].size)

    for idx, row in data.iterrows():
        row[0] = row[0].replace('rt', ' ')

    max_features = 2000
    tokenizer = Tokenizer(num_words=max_features, split=' ')
    tokenizer.fit_on_texts(data['text'].values)

    # save tokenizer
    with open(tokenizer_path, 'wb') as f:
        pickle.dump(tokenizer, f, protocol=pickle.HIGHEST_PROTOCOL)

    X = tokenizer.texts_to_sequences(data['text'].values)
    X = pad_sequences(X)

    embed_dim = 128
    lstm_out = 196

    model = Sequential()
    model.add(Embedding(max_features, embed_dim,input_length = X.shape[1]))
    model.add(SpatialDropout1D(0.4))
    model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(2,activation='softmax'))
    model.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
    logging.info(model.summary())

    Y = pd.get_dummies(data['sentiment']).values
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.33, random_state=42)
    logging.info(f'Training shape: X={X_train.shape}, y={Y_train.shape}')
    logging.info(f'Testing shape: X={X_test.shape}, y={Y_test.shape}')

    batch_size = 32
    model.fit(X_train, Y_train, epochs=7, batch_size=batch_size)
    model.save(model_path)

    if validate:
        validation_size = 1500

        X_validate = X_test[-validation_size:]
        Y_validate = Y_test[-validation_size:]
        X_test = X_test[:-validation_size]
        Y_test = Y_test[:-validation_size]
        score, acc = model.evaluate(X_test, Y_test, verbose = 2, batch_size = batch_size)
        logging.info('Validation score: %.2f' % (score))
        logging.info('Validation accuracy: %.2f' % (acc))

        pos_cnt, neg_cnt, pos_correct, neg_correct = 0, 0, 0, 0
        for x in range(len(X_validate)):

            result = model.predict(X_validate[x].reshape(1, X_test.shape[1]), batch_size=1, verbose=2)[0]

            if np.argmax(result) == np.argmax(Y_validate[x]):
                if np.argmax(Y_validate[x]) == 0:
                    neg_correct += 1
                else:
                    pos_correct += 1

            if np.argmax(Y_validate[x]) == 0:
                neg_cnt += 1
            else:
                pos_cnt += 1

        logging.info(f'Accuracy for positive examples: {pos_correct / pos_cnt * 100}%')
        logging.info(f'Accuracy for negative examples: {neg_correct / neg_cnt * 100}%')


def load_model_and_tokenizer(model_path=DEFAULT_MODEL_FILENAME, tokenizer_path=DEFAULT_TOKENIZER_FILENAME):
    with open(tokenizer_path, 'rb') as handle:
        tokenizer = pickle.load(handle)
    model = load_model(model_path)
    return model, tokenizer


def predict_sentiment(twt_str, model, tokenizer):
    twt = [twt_str]
    # vectorizing the tweet by the pre-fitted tokenizer instance
    twt = tokenizer.texts_to_sequences(twt)
    # padding the tweet to have exactly the same shape as `embedding_2` input
    twt = pad_sequences(twt, maxlen=40, dtype='int32', value=0)
    sentiment = model.predict(twt, batch_size=1, verbose=2)[0]
    return sentiment
    # if (np.argmax(sentiment) == 0):
    #     print("negative")
    # elif (np.argmax(sentiment) == 1):
    #    print("positive")


if __name__ == '__main__':
    model, tokenizer = load_model_and_tokenizer()
    print(predict_sentiment('I spent a nice day with my Mum. We went for lunch and had fun.', model, tokenizer))
    print(predict_sentiment('Using Geon for charity Geon is an exciting blockchain project that plans '
                            'to use augmented reality to help people hit by a natural disaster or caught between either side of a war-zone.',
          model, tokenizer))