""" Views for engineering_exercise

Implementations of the Django REST framework pattern
"""
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets


class UserSerializer(serializers.HyperlinkedModelSerializer):
    """ Serializers define the API representation. """
    class Meta: #pylint: disable=R0903
        """ Configuration for the Serialiser """
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


class UserViewSet(viewsets.ModelViewSet): # pylint: disable=R0901
    """ ViewSets define the view behavior """
    queryset = User.objects.all()
    serializer_class = UserSerializer
