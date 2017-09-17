""" BigTable Management Schema to ITT Project
"""
from google.cloud import bigtable
from oauth2client.client import GoogleCredentials


def create_schema(project_id, instance_id, table_id,
                  column_family, columns=None):
    """ Create a new schema to BigTable

    Args:
        project_id: Id of GCP Project
        instance_id: BigTable instance id
        table_id: just Table id
        columns_family: array with columns family
        columns: dict with columns family as key and
                 columns as values

    Returns:
        True to created or False with error
    """
    try:
        credentials = GoogleCredentials.get_application_default()
        client = bigtable.Client(project=project_id, admin=True)
        instance = client.instance(instance_id)

        table = instance.table(table_id)
        table.create()

        for cols_f in column_family:
            cols = table.column_family(cols_f)
            cols.create()

        return True
    except Exception as error:
        return False, error


if __name__ == '__main__':
    """ Creating the schema of BigTable to ITT project
    """
    table = create_schema(project_id='optimal-oasis-170206',
                          instance_id='itt-develop',
                          table_id='channels',
                          column_family=['BTC', 'USDT', 'XMR', 'ETH'])

    if table is True:
        print('Success!')
    else:
        print('Error: {0}'.format(table))
