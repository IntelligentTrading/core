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
        data: dict with 'row_key', 'column_family',
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

        for col_f in data['data'].keys():

            for col in data['data'][col_f]:
                row.set_cell(col_f, col.encode('utf-8'),
                             data['data'][col_f][col].encode('utf-8'))

        row.commit()

        return True
    except Exception as error:
        return False, error


if __name__ == '__main__':
    """ Insert new data of BigTable to ITT project
    """
    input_json = {
        "row_key": "poloniex#1505851998",
        "data": {
            "BTC": {
                "BTC_ETH_LAST": "0.00000050",
                "BTC_ETH_CHANGE": "0.00000050",
                "BTC_ETH_HIGH": "0.00000050",
                "BTC_ETH_LOW": "0.00000050",
                "BTC_ETH_VOLUME": "0.00000050"
            },
            "USDT": {
                "USDT_ETH_LAST": "0.00000050",
                "USDT_ETH_CHANGE": "0.00000050",
                "USDT_ETH_HIGH": "0.00000050",
                "USDT_ETH_LOW": "0.00000050",
                "USDT_ETH_VOLUME": "0.00000050"
            }
        }
    }

    new_data = input_data(project_id='optimal-oasis-170206',
                          instance_id='itt-develop',
                          table_id='channels',
                          data=input_json)

    if new_data is True:
        print('Success!')
    else:
        print('Error: {0}'.format(new_data))
