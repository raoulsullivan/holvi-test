""" Tests the functionality concerning how engineering_exercise interacts with Accounts objects
"""

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from fintech.models import Account


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
                Account.objects.create(user=user, name='Account {}'.format(j), balance=0)

    @staticmethod
    def test_setup():
        """ Checks the test data has been inserted properly """
        assert User.objects.count() == 11
        assert Account.objects.count() == 20

    def test_account_authentication(self):
        """ Only authenticated users should get in """
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        response = self.client.get(url)
        assert response.status_code == 403
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_account_balance(self):
        """ The balance view should do what it says on the tin """
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        assert response.json() == {
            'uuid': str(account.uuid),
            'balance': '0.00',
        }
