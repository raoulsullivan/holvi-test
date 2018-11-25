""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
import copy
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from fintech.models import Account, Transaction

class AccountBalanceValidationError(serializers.ValidationError):
    pass

def account_balance_validator(value):
    raise AccountBalanceValidationError('derp')


class AccountSerializer(serializers.ModelSerializer):
    """ Serialises the base information regarding an Account """
    class Meta: #pylint: disable=R0903
        """ All fields """
        model = Account
        fields = ('url', 'uuid', 'name', 'user', 'balance')

class AccountBalanceSerializer(serializers.HyperlinkedModelSerializer):
    """ Serialises the Balance information for an Account only. """
    class Meta: #pylint: disable=R0903
        """ Only Balance and UUID """
        model = Account
        fields = ('uuid', 'balance')

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
        #validators = [account_balance_validator]
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


    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None): #pylint: disable=C0103
        """ Retrieves the balance"""
        account = self.get_object()
        serializer = AccountBalanceSerializer(account, many=False)
        return Response(serializer.data)


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
            transaction.save()
            serializer = self.serializer_class(transaction, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get', 'post'])
    def transactions(self, request, pk=None): #pylint: disable=C0103
        """ For interacting with Transactions on this Account
        GET - Retrieves the Transaction listing for the Account
            Ordered with most recently transacted first
        POST - Creates a new Transaction on the Account. Send:
            {
                'transaction_date': '%Y-%m-%d',
                'amount': decimal, 15 digits, 2 decimal places,
                'description': 20 characters,
            }.
        """
        self.serializer_class = TransactionSerializer
        account = self.get_object()

        if request.method == 'POST':
            return self._transactions_post(request, account)

        return self._transactions_get(request, account)
