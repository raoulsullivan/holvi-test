Holvi API exercise submission
===

_Stephen Raoul Sullivan, 2018-11_

This repo is a response to the Holvi transactions API exercise. I've added more words in optional_tasks.md

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

## Using this
### Authentication
All API requests need to come from a Django superuser. You can log in at `http://localhost:8000/` or use the `--user <username>:<password>` arguments for curl

### Django admin
Hop into `/admin` as the superuser and poke around.

### List Accounts
You can't by design. You need to know the UUID of the account.

### Get Account balance
`/account/<uuid>/balance/`. Optional `?date=YY-mm-dd` parameter.

### Get Account transactions
`/account/<uuid>/transactions/`. Transactions are paginated, use `?page=X` parameter.

### Create Transaction
`POST` to `/account/<uuid>/transactions/`. You need to send the `transaction_date`, `amount` and optional `description` parameters.

## TODOs
Thoughts that are not stories, code cleanup, musings for others, etc.
`grep -r -i --include \*.* TODO .`
