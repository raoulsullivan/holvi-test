""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
import datetime
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from fintech.models import Account, Transaction
from fintech.errors import AccountBalanceError

class AccountBalanceValidationError(serializers.ValidationError):
    """ For validation errors involving the Account balance """
    pass


class AccountSerializer(serializers.ModelSerializer):
    """ Serialises the base information regarding an Account """
    class Meta: #pylint: disable=R0903
        """ All fields """
        model = Account
        fields = ('url', 'uuid', 'name', 'user', 'balance')

class TransactionSerializer(serializers.ModelSerializer):
    """ Serialises the base information regarding a Transaction """
    class Meta: #pylint: disable=R0903
        """ All fields """
        model = Transaction
        fields = (
            'uuid',
            'account',
            'transaction_date',
            'amount',
            'description',
            'active',
            'create_time',
            'update_time',
        )
        extra_kwargs = {
            'uuid': {'read_only': True},
            'account': {'read_only': True},
            'active': {'read_only': True},
            'create_time': {'read_only': True},
            'update_time': {'read_only': True},
        }


class AccountViewSet(viewsets.GenericViewSet): # pylint: disable=R0901
    """ Allows users to interact with the Account object"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @staticmethod
    def _calculate_balance_at_date(account, date):
        """ Returns the sum of the amount of all active transactions
        made on or before the date on a given account """
        transactions = Transaction.objects.filter(
            account=account, transaction_date__lte=date, active=True
        ).all()
        balance = sum(x.amount for x in transactions)
        return balance


    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None): #pylint: disable=C0103
        """ Returns the current balance for the Account as a decimal.
        If you specify the 'date' ('%Y-%m-%d') as a query parameter
        it will return the balance at the close of that date."""
        account = self.get_object()
        date_string = request.query_params.get('date')
        if date_string:
            try:
                date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
            except ValueError as err:
                raise serializers.ValidationError(str(err)) from err
            balance = self._calculate_balance_at_date(account, date)
        else:
            balance = account.balance
        return Response(balance)


    def _transactions_get(self, request, account):
        """ Customers may not interact with Transactions that are not 'active'
        TODO - behaviour here dependent on the auth framework.
        We currently assume only staff users, not customers, have access
        """
        if request.user.is_staff:
            query = Transaction.objects.filter(account=account).\
                order_by('-create_time', '-transaction_date')
        else:
            raise NotImplementedError()
            #query = Transaction.objects.filter(account=account, active=True)

        transactions = query.all()

        paginator = PageNumberPagination()
        paginator.page_size = 10
        paginated_queryset = paginator.paginate_queryset(transactions, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


    def _transactions_post(self, request, account):
        """ Creates the transaction object and updates the account balance
        TODO - move the update of account balance to the database model
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            transaction = Transaction(**serializer.validated_data)
            transaction.active = True
            transaction.account = account
            try:
                transaction.save()
            except AccountBalanceError as err:
                raise AccountBalanceValidationError(str(err)) from err
            serializer = self.serializer_class(transaction, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get', 'post'])
    def transactions(self, request, pk=None): #pylint: disable=C0103
        """ For interacting with Transactions on this Account"""
        self.serializer_class = TransactionSerializer
        account = self.get_object()

        if request.method == 'POST':
            return self._transactions_post(request, account)

        return self._transactions_get(request, account)
