# Intelligent Trading Development 
This document describe how works the development and deployment process.

[![Build Status](https://travis-ci.org/IntelligentTrading/IntelligentTrading.svg?branch=master)](https://travis-ci.org/IntelligentTrading/IntelligentTrading)


## Configure GCP
The next steps require the **gcloud** tool, more informations: [gcloud downloads](https://cloud.google.com/sdk/downloads)


Set your account:

`$ gcloud config set account email.account@mydomain.com`

Set the project:

`$ gcloud config set project project-id`

More informations about [Google App Engine](https://cloud.google.com/appengine/docs/python/) standard environment. 


## Testing locally

### Worker Service

Install the dependencies:

`worker/$ pip3.6 install -t lib -r requirements.txt -U` 

**NOTE** if run many times the `pip` do you can insert this argument `--upgrade` 

Start the development server:

`worker/$ python3.6 main.py`

Access the application:

[http://localhost:8080](http://localhost:8080)


### Telegram Service

Install the dependencies:

`telegram/$ pip3.6 install -t lib -r requirements.txt -U` 

**NOTE** if run many times the `pip` do you can insert this argument `--upgrade` 

**TOKEN** will need change the TOKEN in the code: `bot.py`

Start the development server:

`telegram/$ python3.6 bot.py`

Test the application in the Telegram App.


## Deploy to App Engine
Update the jobs of workers:

### Base of All Services

`/$ gcloud app deploy index.yaml cron.yaml`

### Worker Service

`worker/$ gcloud app deploy app.yaml`

### Telegram Service

`telegram/$ gcloud app deploy bot.yaml`
