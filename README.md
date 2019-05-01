[![Build Status](https://travis-ci.com/AustralianSynchrotron/jacow-validator.svg?branch=master)](https://travis-ci.com/AustralianSynchrotron/jacow-validator)

[![codecov](https://codecov.io/gh/AustralianSynchrotron/jacow-validator/branch/master/graph/badge.svg)](https://codecov.io/gh/AustralianSynchrotron/jacow-validator/)

# jacow_validator
Scripts to validate JACoW docx proceedings against the official template.

## Setup using AustralianSynchrotron jacow-validator

    git clone git@github.com:AustralianSynchrotron/jacow-validator.git
    pipenv install --dev
    cd jacow-validator

At time of writing the references.csv file can be accessed at the following:
https://spms.kek.jp/pls/ipac19/references.csv

grab a copy of it and save it to your computer

Create two environment variables:

    URL_TO_JACOW_REFERENCES_CSV=https://spms.kek.jp/pls/ipac19/references.csv
    PATH_TO_JACOW_REFERENCES_CSV=/home/user/Documents/jacow/References.csv

Where **URL_TO_JACOW_REFERENCES_CSV** is set to the currently applicable url
and **PATH_TO_JACOW_REFERENCES_CSV** is set to the location on your filesystem 
where you saved the file. 

##  Setup using forked jacow-validator

1. Fork this project to your own github account

2. Clone your fork to your computer

3. Add the AustralianSynchrotron repo as one of your remote's called "upstream":

    `git remote add upstream https://github.com/AustralianSynchrotron/jacow-validator.git`
    
4. Ensure pipenv is installed:
    
    a. For linux, ensure homebrew is installed - could require a restart

    b. `brew install pipenv`
    
    c. alternatively without homebrew: `pip install pipenv`

1. Ensure your pipenv is running the latest version of python:
    
    1. In a terminal `cd` into your project's directory 
    
    1. `pipenv install python 3.7` (this project makes use of syntax only available in python > 3.5)
    

## Running

(for development mode create a .env file with FLASK_ENV=development)

    pipenv run app

open http://localhost:5000/

### Running in PyCharm

*These steps work for pycharm's community edition which doesn't feature native flask support.*

1. Open pycharm and open the project

2. **File** > **Settings** > *this project* > **project interpreter**

    a. Set the interpreter to use pipenv

3. **Run** > **Edit Configurations** > Add new configuration (`+` button) > Choose Python

    a. Name it jacow-validator or similar
    
    b. Set the script path to point to the flask that is used by your pipenv virtual environment
        
        1. You can find the location of your virtual environment's files using the command `pipenv --venv` ran from within your project directory
        
        1. Your flask script will be located within a **bin** folder at that location so if `pipenv --venv` outputs:
            
            /home/*user*/.local/share/virtualenvs/jacow-validator-Awl2i6Az/
            
            then you will need to enter into the script path field: 
            
            /home/*user*/.local/share/virtualenvs/jacow-validator-Awl2i6Az/bin/flask
    
    c. In the parameters type `run`
    
    d. Add a new environment variable called **FLASK_APP** and set it to the path to the app.py file in src/jacowvalidator:
    
        example: FLASK_APP=/home/*user*/apps/jacow-validator/src/jacowvalidator/app.py

4. Hitting the (play) or (debug) buttons in pycharm should now work to launch the app which you should now be able to see at http://localhost:5000/ 

## Testing
    
    pipenv run tox

## Testing in PyCharm

from within your project directory:

`pipenv run tox`

or simply `tox` if you've already activated your virtual environment.
