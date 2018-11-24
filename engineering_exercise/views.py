""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
from rest_framework import serializers, viewsets

from fintech.models import Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializers define the API representation. """
    class Meta: #pylint: disable=R0903
        """ Configuration for the Serialiser """
        model = Account
        fields = ('url', 'uuid', 'balance')


class AccountViewSet(viewsets.ModelViewSet): # pylint: disable=R0901
    """ ViewSets define the view behavior """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
