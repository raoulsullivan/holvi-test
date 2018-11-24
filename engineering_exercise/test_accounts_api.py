from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from fintech.models import Account


class AccountViewsTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(username='Superuser', is_staff=True, password='derp', email='stephen@saruste.fi')
        for i in range(10):
            user = User.objects.create_user(username='Test user {}'.format(i))
            for j in range(2):
                Account.objects.create(user=user, name='Account {}'.format(j), balance=0)

    def test_setup(self):
        assert User.objects.count() == 11
        assert Account.objects.count() == 20

    def test_account_authentication(self):
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        response = self.client.get(url)
        assert response.status_code == 403
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        assert response.status_code == 200

    def test_account_list_disabled(self):
        url = reverse('account-list')
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        assert response.status_code == 404

    def test_account_retrieve_disabled(self):
        account = Account.objects.first()
        url = reverse('account-detail', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        assert response.status_code == 404

    def test_account_balance(self):
        account = Account.objects.first()
        url = reverse('account-balance', args=(account.uuid,))
        self.client.login(username=self.superuser.username, password='derp')
        response = self.client.get(url)
        assert response.json() == {
            'uuid': str(account.uuid),
            'balance': '0.00',
        }