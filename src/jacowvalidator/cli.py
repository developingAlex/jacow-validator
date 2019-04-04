import click
from flask import Flask
from flask.cli import FlaskGroup

def create_app():
    from .app import app
    return app

@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the JACoW application."""