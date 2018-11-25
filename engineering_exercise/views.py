""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from fintech.models import Account, Transaction


class AccountSerializer(serializers.HyperlinkedModelSerializer):
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
            'update_time'
        )


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

    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None): #pylint: disable=C0103
        """ Retrieves the transaction listing for the account
        Ordered with most recently transacted first
        """
        account = self.get_object()

        # Users may not interact with Transactions that are not 'active'
        # TODO - behaviour here dependent on the auth framework.
        # We currently assume only staff users have access
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
        serializer = TransactionSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
