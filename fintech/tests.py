""" Tests for fintech app """

import datetime
from decimal import Decimal
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.models import User

from .errors import AccountBalanceError
from .models import Account, Transaction


class TestTransactionAmountProtection(TestCase):
    """ Tests the business logic protecting Transactions and Accounts
    Tests methods transaction.save and account.update_balance, calculated_balance together.
    Could split these out into more explicit tests with mocking
    """
    def setUp(self):
        """ A small set of test data """
        user = User.objects.create_user(username='Test user')
        self.account = Account.objects.create(user=user, name='Test account', balance=0)

    def test_transaction_creation(self):
        """ Transaction should increase Account balance """
        transaction_amount = Decimal('10.32')
        Transaction.objects.create(
            account=self.account,
            transaction_date=datetime.datetime.today().date(),
            amount=transaction_amount,
            active=True,
            description='Test transaction',
        )
        self.assertEqual(self.account.balance, transaction_amount)

    def test_transaction_active(self):
        """ Only active transactions should affect balance """
        transaction_amount = Decimal('10.32')
        for i in range(2):
            active = True
            if i == 2:
                active = False
            Transaction.objects.create(
                account=self.account,
                transaction_date=datetime.datetime.today().date(),
                amount=transaction_amount,
                active=active,
                description='Test transaction',
            )
        self.assertEqual(self.account.balance, (transaction_amount * 2))

    def test_cannot_create_illegal_transaction(self):
        """ Transactions cannot be created if they take account balance below 0 """
        transaction_amount = Decimal('-10.32')
        with self.assertRaises(AccountBalanceError):
            Transaction.objects.create(
                account=self.account,
                transaction_date=datetime.datetime.today().date(),
                amount=transaction_amount,
                active=True,
                description='Test transaction',
            )
        self.assertEqual(self.account.balance, 0)
        self.assertEqual(Transaction.objects.count(), 0)


class TestPopulateSampleDataCommand(TestCase):
    def test_populate_sample_data_command(self):
        call_command('populate_sample_data', number_customers=3, accounts_per_customer=3, transactions_per_account=3)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Account.objects.count(), 9)
        self.assertEqual(Transaction.objects.count(), 27)