import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import errorcode

def ittconnection(DATABASE='prodcopy'):
    if DATABASE == 'prod':
        config = {
            'user': 'alienbaby',
            'password': 'alienbabymoonangel',
            'host': 'intelligenttrading-aurora-production-primary-cluster.cluster-caexel1tmds5.us-east-1.rds.amazonaws.com',
            'port': '3306',
            'database': 'intelligenttrading_primary',
            'raise_on_warnings': True,
        }
        try:
            db_connection = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    elif DATABASE == 'stage':
        config = {
            'user': 'alienbaby',
            'password': 'alienbabymoonangel',
            'host': 'intelligenttrading-aurora-production-postgres-cluster.cluster-caexel1tmds5.us-east-1.rds.amazonaws.com',
            'port': '5432',
            'dbname': 'primary_postgres'
        }

        try:
            db_connection = pg.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    elif DATABASE == 'prodcopy':
        config = {
            'user': 'alienbaby',
            'password': 'alienbabymoonangel',
            'host': 'prodclone.caexel1tmds5.us-east-1.rds.amazonaws.com',
            'port': '3306',
            'database': 'intelligenttrading_primary',
            'raise_on_warnings': True,
        }

        try:
            db_connection = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    return db_connection


def get_resampled(db_connection, transaction_coin, counter_coin, resample_period):
    query = (" SELECT * FROM indicator_priceresampl WHERE \
    transaction_currency='%s' AND \
    counter_currency=%d \
    and resample_period=%d ") % (transaction_coin, counter_coin, resample_period)

    resampl_df = pd.read_sql(query, con=db_connection)
    resampl_df['timestamp'] = pd.to_datetime(resampl_df['timestamp'], unit='s')
    resampl_df.index = pd.DatetimeIndex(resampl_df.timestamp)
    resampl_df.sort_index(inplace=True)
    return resampl_df


def get_raw_price(db_connection, transaction_coin, counter_coin):
    query = "SELECT * FROM indicator_price WHERE transaction_currency='%s' AND counter_currency=%d "
    query = query % (transaction_coin, counter_coin)
    df_sql = pd.read_sql(query, con=db_connection)
    df_sql['timestamp'] = pd.to_datetime(df_sql['timestamp'], unit='s')
    df_sql.index = pd.DatetimeIndex(df_sql.timestamp)

    return df_sql["price"].to_frame()


def get_raw_volume(db_connection, transaction_coin, counter_coin):
    query = "SELECT * FROM indicator_volume WHERE transaction_currency='%s' AND counter_currency=%d "
    query = query % (transaction_coin, counter_coin)
    df_sql = pd.read_sql(query, con=db_connection)
    df_sql['timestamp'] = pd.to_datetime(df_sql['timestamp'], unit='s')
    df_sql.index = pd.DatetimeIndex(df_sql.timestamp)

    return df_sql["volume"].to_frame()


# REGRESSION: dataset for regression: split one continues timeseries inro many subsets by striding
def regression_dataset_from_ts(data_df, win_size, stride, future, label_type):
    n = len(data_df)
    num_examples = int((n - win_size) / stride)

    # (4968, 96, 1)
    predictors = data_df.shape[1]  # make prediction based on multivatiate ts, price and volume

    data_set = np.zeros([num_examples, win_size, predictors])
    labels = np.zeros([num_examples, 1])
    prices = np.zeros([num_examples, 1])

    for ex in range(0, num_examples):
        one_example_0 = data_df[ex:ex + win_size]['price'].values.reshape([-1, 1])
        one_example_1 = data_df[ex:ex + win_size]['volume'].values.reshape([-1, 1])
        one_example_2 = data_df[ex:ex + win_size]['price_var'].values.reshape([-1, 1])
        one_example_3 = data_df[ex:ex + win_size]['volume_var'].values.reshape([-1, 1])
        last_price = one_example_0[-1, 0]

        data_set[ex, :, 0] = one_example_0[:, 0]
        data_set[ex, :, 1] = one_example_1[:, 0]
        data_set[ex, :, 2] = one_example_2[:, 0]
        data_set[ex, :, 3] = one_example_3[:, 0]

        future_prices = data_df[ex + win_size:ex + win_size + future]['price'].values
        open_price = future_prices[0]
        close_price = future_prices[-1]
        price_return = close_price - open_price
        percentage_return = 1 - (last_price - price_return) / last_price

        if label_type == "price":
            label = open_price

        if label_type == "return":
            label = price_return

        delta = 0.03
        if label_type == "percent_return":
            label = 0 if (abs(percentage_return) < delta) else np.sign(percentage_return)

        labels[ex, :] = label
        prices[ex, :] = open_price

    return data_set, labels, prices


def classification_dataset_from_ts(data_df, win_size, stride, future, delta):
    n = len(data_df)
    num_examples = int((n - win_size) / stride)

    # (4968, 96, 1)
    predictors = data_df.shape[1]  # make prediction based on multivatiate ts, price and volume

    data_set = np.zeros([num_examples, win_size, predictors])
    labels = np.zeros([num_examples, 3])
    prices = np.zeros([num_examples, 1])

    for ex in range(0, num_examples):
        one_example_0 = data_df[ex:ex + win_size]['price'].values.reshape([-1, 1])
        one_example_1 = data_df[ex:ex + win_size]['volume'].values.reshape([-1, 1])
        one_example_2 = data_df[ex:ex + win_size]['price_var'].values.reshape([-1, 1])
        one_example_3 = data_df[ex:ex + win_size]['volume_var'].values.reshape([-1, 1])
        last_price = one_example_0[-1, 0]

        future_prices = data_df[ex + win_size:ex + win_size + future]['price'].values
        open_price = future_prices[0]
        close_price = future_prices[-1]
        price_return = close_price - open_price
        percentage_return = 1 - (last_price - price_return) / last_price

        label = 0 if (abs(percentage_return) < delta) else np.sign(percentage_return)

        data_set[ex, :, 0] = one_example_0[:, 0]
        data_set[ex, :, 1] = one_example_1[:, 0]
        data_set[ex, :, 2] = one_example_2[:, 0]
        data_set[ex, :, 3] = one_example_3[:, 0]

        prices[ex, :] = open_price

        # 0 - same / 1 - up / 2 - down
        if label == 0:
            labels[ex, 0] = 1
        elif label == 1:
            labels[ex, 1] = 1
        elif label == -1:
            labels[ex, 2] = 1

    return data_set, labels, prices


def accuracy(predictions, labels):
    return (100.0 * np.sum(np.argmax(predictions, 1) == np.argmax(labels, 1)) / predictions.shape[0])


def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)
