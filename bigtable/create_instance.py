""" BigTable Management Instances to ITT Project
"""
from google.cloud import bigtable
from oauth2client.client import GoogleCredentials


def create_instance(project_id, instance_id, location_id, display_name,
                    serve_nodes):
    """ Wraper to create a new BigTable instance on GCP
    
    Args:
        project_id: Id of GCP Project
        instance_id: BigTable instance id
        location_id: Location to run BigTable instance
        display_name: BigTable display name
        serve_nodes: number of servers, default is 3

    Returns:
        True to created or False with error
    """
    try:
        credentials = GoogleCredentials.get_application_default()
        client = bigtable.Client(project=project_id, admin=True)

        instance = client.instance(instance_id, location_id, display_name, serve_nodes)
        instance.create()
        return True
    except Exception as error:
        return False, error


if __name__ == '__main__':
    """ Creating the development environment to ITT project
    """
    result = create_instance(project_id='optimal-oasis-170206',
                             instance_id='itt-develop',
                             location_id='us-east1-b',
                             display_name='ITT Development Env',
                             serve_nodes=3)

    if result is True:
        print('Success!')
    else:
        print('Error: {0}'.format(result))
