""" Tests the functionality concerning how engineering_exercise interacts with Accounts objects
"""
import copy
import datetime
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from fintech.models import Account, Transaction


TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

class AccountViewsTestCase(TestCase):
    """ Tests for the Account API Views """

    def setUp(self):
        """ A small set of test data """
        self.superuser = User.objects.create_superuser(
            username='Superuser', is_staff=True, password='derp', email='stephen@saruste.fi'
        )
        for i in range(10):
            user = User.objects.create_user(username='Test user {}'.format(i))
            for j in range(2):
                account = Account.objects.create(user=user, name='Account {}'.format(j), balance=0)
                for k in range(5):
                    transaction_date = datetime.datetime.today().date() - datetime.timedelta(days=k)
                    Transaction.objects.create(
                        account=account,
                        transaction_date=transaction_date,
                        amount=1,
                        active=True,
                        description='Transaction {}'.format(k),
                    )

    def test_setup(self):
        """ Checks the test data has been inserted properly """
        self.assertEqual(User.objects.count(), 11)
        self.assertEqual(Account.objects.count(), 20)
        self.assertEqual(Transaction.objects.count(), 100)

    def test_account_authentication(self):
        """ Only authenticated users should get in """
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_account_balance(self):
        """ The balance view should do what it says on the tin """
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        expected_response = Decimal('5.00')
        self.assertEqual(response.json(), expected_response)

    def test_account_balance_at_date(self):
        """ The balance view should do what it says on the tin """
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url, {'date': '2020-10-a'})
        self.assertEqual(response.status_code, 400)
        today = datetime.datetime.today().date()
        response = self.client.get(url, {'date': str(today)})
        expected_response = Decimal('5.00')
        self.assertEqual(response.json(), expected_response)
        today_minus_3 = today - datetime.timedelta(days=3)
        response = self.client.get(url, {'date': str(today_minus_3)})
        expected_response = Decimal('2.00')
        self.assertEqual(response.json(), expected_response)

    def test_transactions_get(self):
        """ Should get a list of serialised transactions """
        account = Account.objects.first()
        url = reverse('account-transactions', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 5)
        # Should get the most recent transaction *first*
        most_recent_transaction = account.transactions.order_by(
            '-create_time', '-transaction_date'
        ).first()
        expected_response = {
            'uuid': str(most_recent_transaction.uuid),
            'account': str(account.uuid),
            'transaction_date': datetime.datetime.today().date().isoformat(),
            'amount': '1.00',
            'description': 'Transaction 4',
            'active': True,
            'create_time': most_recent_transaction.create_time.strftime(TIMESTAMP_FORMAT),
            'update_time': most_recent_transaction.update_time.strftime(TIMESTAMP_FORMAT),
        }
        self.assertEqual(response.json()['results'][0], expected_response)

    def test_transactions_post(self):
        """ Should create the transaction and return the serialised representation """
        account = Account.objects.first()
        old_balance = copy.copy(account.balance)
        url = reverse('account-transactions', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')

        new_transaction_date = datetime.datetime.today().date() - datetime.timedelta(days=5)
        new_transaction_amount_string = '-3.30'
        new_transaction_amount_float = float(new_transaction_amount_string)
        new_transaction_amount_decimal = Decimal(new_transaction_amount_string)
        new_transaction_description = 'New transaction'
        new_transaction_data = {
            'transaction_date': new_transaction_date,
            'amount': new_transaction_amount_float,
            'description': new_transaction_description
        }
        response = self.client.post(url, data=new_transaction_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Transaction.objects.count(), 101)

        # Check properties, especially 'amount'
        new_transaction = Transaction.objects.latest('create_time')
        serialised_transaction = response.json()
        self.assertEqual(serialised_transaction['uuid'], str(new_transaction.uuid))
        self.assertEqual(serialised_transaction['account'], str(account.uuid))
        self.assertEqual(
            serialised_transaction['transaction_date'],
            new_transaction_date.isoformat()
        )
        self.assertEqual(serialised_transaction['description'], new_transaction_description)
        self.assertEqual(serialised_transaction['amount'], new_transaction_amount_string)

        # And check account balance is updated
        expected_balance = old_balance + new_transaction_amount_decimal
        self.assertEqual(new_transaction.account.balance, expected_balance)

    def test_illegal_transaction_post(self):
        """ Transaction that takes account balance negative should fail to POST """
        account = Account.objects.first()
        old_balance = copy.copy(account.balance)
        url = reverse('account-transactions', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')

        new_transaction_date = datetime.datetime.today().date() - datetime.timedelta(days=5)
        new_transaction_amount_string = '-300.30'
        new_transaction_amount_float = float(new_transaction_amount_string)
        new_transaction_description = 'New transaction'
        new_transaction_data = {
            'transaction_date': new_transaction_date,
            'amount': new_transaction_amount_float,
            'description': new_transaction_description
        }
        response = self.client.post(url, data=new_transaction_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Transaction.objects.count(), 100)
        self.assertEqual(account.balance, old_balance)
