""" BigTable Reference
"""
from google.cloud import bigtable


""" At Google AppEngine or Google Compute Engine have auto detect auth
    and credentials
"""
client = bigtable.Client(project="optimal-oasis-170206", admin=True)

"""Some informations about the `client` 
"""
print('Name of project: \t\t%s' % client.project)
print('Name of agent connected: \t%s' % client.user_agent)
print('Client ID: \t\t\t%s' % client.credentials.client_id)
print('Client Secret: \t\t\t%s' % client.credentials.client_secret)

instance = client.instance(instance_id='itt-test', location='us-east1-b',
                           display_name='ITT Test')
instance.reload()

"""Some informations about the `instance`
"""
print('Instance Name: \t\t\t%s' % instance.name)
print('Instance ID: \t\t\t%s' % instance.instance_id)

table = instance.table('apps')
column_families = table.list_column_families()

print('Table: \t\t\t\t%s' % table.name)
print('Column Families: \t\t%s' % column_families)
