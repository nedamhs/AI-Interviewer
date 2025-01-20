from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.
class Profile(models.Model):
    """ Abstract user profile for talent, company reps, and admins
    """
    # TODO: implement current location as part of profile
    #       city name, country code (available in zoneinfo? or google palce autocomplete)
    #       also: city, state/province, postal code, country/region
    # Possibly better to use google API here #} we want to be able to calculate distances

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    last_modified = models.DateTimeField(auto_now=True)

    # methods
    def __str__(self):
        return f"{self.user.email} profile"



class Employee(models.Model):
    DEPARTMENT_CHOICES = (
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('engineering', 'Engineering'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='employees')
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    salary = models.PositiveIntegerField()


# Example serializer
from rest_framework import serializers

class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    department = serializers.ChoiceField(choices=Employee.DEPARTMENT_CHOICES)

    class Meta:
        model = Employee
        fields = ('id', 'user', 'name', 'department', 'salary')