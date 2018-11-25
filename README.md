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


## Change control
No external changes possible - this is a repo for an interview test, not an actual project!


## Coding style
PEP8
Pylintrc included `pylint --load-plugins pylint_django engineering_exercise/`


## Tests
Uses django test framework (unittest) `python manage.py test engineering_exercise fintech`


## Running the project
It's Django, so:
1. Get your database set up
1. Change to your virtual environment
1. Create a superuser `python manage.py createsuperuser`
1. Populate some sample data `python manage.py populate_sample_data`
1. Start the server `python manage.py runserver`
1. Navigate to `http://localhost:8000/`
1. Log in as the superuser
1. Navigate to `http://localhost:8000/account/<UUID>/balance/`


## TODOs
Thoughts that are not stories, code cleanup, musings for others, etc.
`grep -r -i --include \*.* TODO .`
