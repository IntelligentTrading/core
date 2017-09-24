""" BigTable Inserting Data to ITT Project
"""
from google.cloud import bigtable
from oauth2client.client import GoogleCredentials


def read_data(project_id, instance_id, table_id, data):
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

        #key = 'poloniex#1505851997'

        #row = table.read_row(key.encode('utf-8'))
        #print(row)
        
        #value = row.cells['BTC']['BTC_ETH_CHANGE'][0].value
        #print('\t{}: {}'.format(key, value.decode('utf-8')))

        COLUMN_FAMILY_NAME = 'BTC'
        COLUMN_NAME = 'BTC_ETH_CHANGE'

        #print('Scan for all greetings:')
        #for row in table.read_rows():
        #    print(row.cells[COLUMN_FAMILY_NAME][COLUMN_NAME.encode('UTF-8')][0].decode('UTF-8'))

        
        print('Scanning for all greetings:')
        partial_rows = table.read_rows()
        partial_rows.consume_all()

        for row_key, row in partial_rows.rows.items():
            key = row_key.decode('utf-8')
            cell = row.cells[COLUMN_FAMILY_NAME][COLUMN_NAME.encode('UTF-8')][0]
            value = cell.value.decode('utf-8')
            print('\t{}: {}'.format(key, value))
        

        return True
    except Exception as error:
        return False, error


if __name__ == '__main__':
    """ Creating the schema of BigTable to ITT project
    """
    query = read_data(project_id='optimal-oasis-170206',
                      instance_id='itt-develop',
                      table_id='channels',
                      data="")

    if query is True:
        print('Success!')
    else:
        print('Error: {0}'.format(query))
