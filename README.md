# jacow_validator
Scripts to validate JACoW docx proceedings against the official template

## Get started developing

### Fork, clone and setup pipenv

1. Fork this project to your own github account

1. Clone your fork to your computer

1. Add the AustralianSynchrotron repo as one of your remote's called "upstream":

    `git remote add upstream https://github.com/AustralianSynchrotron/jacow-validator.git`

1. Ensure pipenv is installed:
    
    1. Ensure homebrew is installed - could require a restart

    1. `brew install pipenv`
    
    1. alternatively without homebrew: `pip install pipenv`

1. Ensure your pipenv is running the latest version of python:
    
    1. In a terminal `cd` into your project's directory 
    
    1. `pipenv install python 3.7` (this project makes use of syntax only available in python > 3.5)
    

### Set up pycharm to run the app

*These steps work for pycharm's community edition which doesn't feature native flask support.*

1. Open pycharm and open the project

1. **File** > **Settings** > *this project* > **project interpreter**

    1. Set the interpreter to use pipenv

1. **Run** > **Edit Configurations** > Add new configuration (`+` button) > Choose Python

    1. Name it jacow-validator or similar
    
    1. Set the script path to point to the flask that is used by your pipenv virtual environment
        
        1. You can find the location of your virtual environment's files using the command `pipenv --venv` ran from within your project directory
        
        1. Your flask script will be located within a **bin** folder at that location so if `pipenv --venv` outputs:
            
            /home/*user*/.local/share/virtualenvs/jacow-validator-Awl2i6Az/
            
            then you will need to enter into the script path field: 
            
            /home/*user*/.local/share/virtualenvs/jacow-validator-Awl2i6Az/bin/flask
    
    1. In the parameters type `run`
    
    1. Add a new environment variable called **FLASK_APP** and set it to the path to the app.py file in src/jacowvalidator:
    
        example: FLASK_APP=/home/*user*/apps/jacow-validator/src/jacowvalidator/app.py

1. Hitting the (play) or (debug) buttons in pycharm should now work to launch the app which you should now be able to see at http://localhost:5000/ 

## Running tests:

from within your project directory:

`pipenv run tox`

or simply `tox` if you've already activated your virtual environment.
