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
