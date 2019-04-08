[![Build Status](https://travis-ci.com/AustralianSynchrotron/jacow-validator.svg?branch=master)](https://travis-ci.com/AustralianSynchrotron/jacow-validator)

# jacow_validator
Scripts to validate JACoW docx proceedings against the official template.

## Setup

    git clone git@github.com:AustralianSynchrotron/jacow-validator.git
    cd jacow-validator
    pipenv install --dev

## Running

(for development mode create a .env file with FLASK_ENV=development)

    pipenv run app

open http://localhost:5000/

## Testing
    
    pipenv run tox
