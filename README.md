Holvi API exercise submission
===

_Stephen Raoul Sullivan, 2018-11_

This repo is a response to the Holvi transactions API exercise. The specific tasks covered are:




## Python environment setup and installation

### Virtual environment
It's highly recommended to use a virtual environment to ensure consistency.
Please read about pyenv or similar for your environment if this is new to you.

### Python version
The project was built in Python 3.4.6

### Required packages
See requirements.txt, but it's Django


## Database
SQLlite.
1. Use `python manage.py migrate` to set up.
2. Create an initial user with `python manage.py createsuperuser`


## Change control
No external changes possible - this is a repo for an interview test, not an actual project!


## Coding style
PEP8
Pylintrc included


## Tests
Uses pytest and pytest-cov `pytest --cov=engineering_exercise`


## Running the project
It's Django, so:
1. Change to your virtual environment
2. `python manage.py runserver`