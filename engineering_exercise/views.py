""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
from rest_framework import serializers, viewsets, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from fintech.models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializers define the API representation. """
    class Meta: #pylint: disable=R0903
        """ Configuration for the Serialiser """
        model = Account
        fields = ('url', 'uuid', 'balance')

class AccountBalanceSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializers define the API representation. """
    class Meta: #pylint: disable=R0903
        """ Configuration for the Serialiser """
        model = Account
        fields = ('uuid', 'balance')


class AccountViewSet(viewsets.ReadOnlyModelViewSet): # pylint: disable=R0901
    """ Allows users to interact with the Account objet"""
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def list(self, request):
        # No use case yet, overridden
        raise exceptions.NotFound()

    def retrieve(self, request, pk):
        # No use case yet, overridden
        raise exceptions.NotFound()

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        account = self.get_object()
        serializer = AccountBalanceSerializer(account, many=False)
        return Response(serializer.data)
