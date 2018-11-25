""" Handles the population of sample data """
import datetime
import random
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from fintech.models import Account, Transaction

MAX_TRANSACTION_AGE_DAYS = 365

class Command(BaseCommand):
    """ Handles the population of sample data """

    def add_arguments(self, parser):
        parser.add_argument(
            '-c',
            '--number_customers',
            type=int,
            help='The number of customers to create. Defaults to 10',
            metavar='[1-100]',
            choices=range(1, 101),
            default=10,
        )
        parser.add_argument(
            '-a',
            '--accounts_per_customer',
            type=int,
            help='The number of accounts per customer to create. Defaults to 2',
            metavar='[1-5]',
            choices=range(1, 6),
            default=2,
        )
        parser.add_argument(
            '-t',
            '--transactions_per_account',
            type=int,
            help='The number of transactions per account to create. Defaults to 5',
            metavar='[1-50]',
            choices=range(1, 51),
            default=5,
        )

    @staticmethod
    def _generate_transaction_date(index, days_interval):
        # Puts a bit of noise in the transaction date
        day_fuzz = random.randint(0, days_interval)
        day_delta = MAX_TRANSACTION_AGE_DAYS - ((days_interval * index) + day_fuzz)
        transaction_date = datetime.datetime.today().date() - \
            datetime.timedelta(days=day_delta)
        return transaction_date

    def handle(self, *args, **options):
        days_interval = round(MAX_TRANSACTION_AGE_DAYS / options['transactions_per_account'])

        with transaction.atomic():
            for i in range(options['number_customers']):
                user = User.objects.create(username='Sample User {}'.format(i))

                for j in range(options['accounts_per_customer']):
                    account = Account.objects.create(
                        user=user,
                        name='Sample Account {}'.format(j),
                        balance=0
                    )
                    running_balance = 0

                    for k in range(options['transactions_per_account']):
                        transaction_date = self._generate_transaction_date(k, days_interval)

                        # And into the amount
                        transaction_amount = Decimal(random.randint(1, 100001)) / 100
                        if running_balance > transaction_amount:
                            # Will throw in some negative transactions if possible
                            transaction_amount = transaction_amount * -1
                        running_balance += transaction_amount

                        Transaction.objects.create(
                            account=account,
                            transaction_date=transaction_date,
                            amount=transaction_amount,
                            active=True,
                            description='Sample Transaction {}'.format(k),
                        )

        self.stdout.write('Objects created')
