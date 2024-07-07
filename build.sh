#!usr/bin/env bash

#install modules 
pip install -r requirements.txt


python manage.py collectstatic --no-input 

python manage.py migrate