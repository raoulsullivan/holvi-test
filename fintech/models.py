""" Models for the fintech app """
import uuid
from django.db import models, transaction

from .errors import AccountBalanceError


class Account(models.Model):
    """
    Represents a bank account in the system.

    The users of Account and Transaction model should make sure that the
    following conditions are always True:
        account.balance == sum(
           t.amount for t in account.transactions.all() if t.active
        )
        account.balance >= 0
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=20)
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    # TODO - decimals probably a bad idea - store int instead
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)

    def update_balance(self):
        """ Refreshes the balance from calculated_balance """
        if self.calculated_balance < 0:
            raise AccountBalanceError('calculated_balance on account {} is below 0'.format(self))
        self.balance = self.calculated_balance
        self.save()

    @property
    def calculated_balance(self):
        """ Calculates the balance from active related Transactions """
        return sum(x.amount for x in self.transactions.all() if x.active)


class Transaction(models.Model):
    """
    Records transactions on account. You can think of these as entries
    on account statement.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account = models.ForeignKey(
        Account, related_name='transactions',
        on_delete=models.PROTECT)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=20, blank=True, default='')

    # If active is False, the transaction should not be visible to the
    # customer in any way.
    active = models.BooleanField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs): #pylint: disable=W0221
        """ Checks if a Transaction will bring the Account balance below 0 before save """
        existing_balance = self.account.calculated_balance
        if (existing_balance + self.amount) < 0:
            raise AccountBalanceError(
                'Balance of account {} would be brought below 0'.format(self.account)
            )
        instance = super().save(*args, **kwargs) #pylint: disable=E1128
        transaction.on_commit(self.account.update_balance())
        return instance
