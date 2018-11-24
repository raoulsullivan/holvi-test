from django.test import TestCase
from django.contrib.auth.models import User

from fintech.models import Account


class AccountViewsTestCase(TestCase):
    def setUp(self):
        for i in range(10):
            user = User.objects.create(username='Test user {}'.format(i))

    def test_account_authentication(self):
        assert User.objects.count() == 10