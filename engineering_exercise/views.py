""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
from rest_framework import serializers, viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from fintech.models import Account


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


class AccountViewSet(viewsets.ReadOnlyModelViewSet): # pylint: disable=R0901
    """ Allows users to interact with the Account object"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request, *args, **kwargs):
        # No use case yet, overridden
        raise exceptions.NotFound()

    def retrieve(self, request, *args, **kwargs):
        # No use case yet, overridden
        raise exceptions.NotFound()

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None): #pylint: disable=C0103
        """ Retrieves the balance"""
        account = self.get_object()
        serializer = AccountBalanceSerializer(account, many=False)
        return Response(serializer.data)
