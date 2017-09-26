# Documentation about ITT environment 
In this document we'll share how create and use our environment on Google Cloud Platform.


# gcloud
This tool is important to create, managment and publish our infrastructure on GCP.

## Install
[How to install gcloud tool](https://cloud.google.com/sdk/downloads)

## Update
`$ gcloud components update`

## Components
`$ gcloud components install cbt bigtable bq kubectl`


# Bigtable
Is necessary create the BigTable into GCP console. 
In this step will create a development environment to implement a new feature

## Create a instance
Reference: [How-to create a BigTable instance](https://cloud.google.com/bigtable/docs/quickstart-cbt)

## Configure cbt tool
insert the project-id in the config file:
`$ echo project = optimal-oasis-170206 > ~/.cbtrc`

insert the instance-id of BigTable created on GCP console:
`$ echo instance = itt-test >> ~/.cbtrc`

insert the ITT service account created on GCP console. The Cloud Bigtable Admin API should be enabled:
`$ echo creds = /Users/firemanxbr/GitHub/data-sources/credentials.json >> ~/.cbtrc`
