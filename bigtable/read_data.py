""" BigTable Inserting Data to ITT Project
"""
from google.cloud import bigtable
from oauth2client.client import GoogleCredentials


def read_data(project_id, instance_id, table_id, column_family,
              column, start_row_key=None, end_row_key=None):
    """ Input new data into BigTable

    Args:
        project_id: Id of GCP Project
        instance_id: BigTable instance id
        table_id: just Table id
        column_family: column family name
        column: column name
        start_row_key: start name of row key (optional)
        end_row_key: end name of row key (optional)

    Returns:
        Dictionary with row keys and values or None
    """
    try:
        GoogleCredentials.get_application_default()
        client = bigtable.Client(project=project_id, admin=True)
        instance = client.instance(instance_id)

        table = instance.table(table_id)

        partial_rows = table.read_rows(start_key=start_row_key,
                                       end_key=end_row_key)
        partial_rows.consume_all()

        values = {}

        for row_key, row in partial_rows.rows.items():
            key = row_key.decode('utf-8')
            cell = row.cells[column_family][column.encode('UTF-8')][0]
            value = cell.value
            values[key] = value

        return values
    except Exception as error:
        return False, error


if __name__ == '__main__':
    """ Search the data of BigTable to ITT project (example)
    """
    query = read_data(project_id='optimal-oasis-170206',
                      instance_id='itt-develop',
                      table_id='channels',
                      column_family="BTC",
                      column="BTC_XCP_LAST",
                      start_row_key="poloniex#1507238652",
                      end_row_key="")

    print(query)
