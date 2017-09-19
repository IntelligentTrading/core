""" BigTable Inserting Data to ITT Project
"""
from google.cloud import bigtable
from oauth2client.client import GoogleCredentials


def input_data(project_id, instance_id, table_id, data):
    """ Input new data into BigTable

    Args:
        project_id: Id of GCP Project
        instance_id: BigTable instance id
        table_id: just Table id
        columns_family: array with columns family
        data: dict with 'column_family', 'row_key',
              'columns' and 'values'

    Returns:
        True to inserted or False with error
    """
    try:
        GoogleCredentials.get_application_default()
        client = bigtable.Client(project=project_id, admin=True)
        instance = client.instance(instance_id)

        table = instance.table(table_id)

        row = table.row(data['row_key'])

        for column_family in data['data']:


        """
        => row.set_cell(column_family[0], col_id1, value1.encode('utf-8'))
        => row.commit()
        """

        return True
    except Exception as error:
        return False, error


if __name__ == '__main__':
    """ Creating the schema of BigTable to ITT project
    """
    data = {
        "row_key": "poloniex#1505851997",
        "data": [{
            "BTC": {
                "BTC_ETH_LAST": 0.00000043,
                "BTC_ETH_CHANGE": 0.00000044,
                "BTC_ETH_HIGH": 0.00000045,
                "BTC_ETH_LOW": 0.00000046,
                "BTC_ETH_VOLUME": 0.00000047
            },
            "USDT": {
                "USDT_ETH_LAST": 0.00000043,
                "USDT_ETH_CHANGE": 0.00000044,
                "USDT_ETH_HIGH": 0.00000045,
                "USDT_ETH_LOW": 0.00000046,
                "USDT_ETH_VOLUME": 0.00000047
            }
        }]
    }

    new_data = input_data(project_id='optimal-oasis-170206',
                          instance_id='itt-develop',
                          table_id='channels',
                          data=data)

    if new_data is True:
        print('Success!')
    else:
        print('Error: {0}'.format(new_data))
