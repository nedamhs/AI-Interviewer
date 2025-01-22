from django.db import models

class LocationDetails(models.Model):
    """Details of a location fetched from Google Maps API"""

    formatted_address = models.CharField(max_length=1000, null=True, blank=True)

    latitude = models.FloatField()

    longitude = models.FloatField()

    def __str__(self):
        return self.formatted_address


class Location(models.Model):
    """Base location model storing user-defined location information"""

    # lower-case user input
    label = models.CharField(max_length=1000)

    details = models.ForeignKey(
        LocationDetails, null=True, on_delete=models.deletion.SET_NULL
    )

    @property
    def display_name(self):
        """
        Returns a string given a Location Object
        if the details.formatted_address field is present, return it;
        otherwise, return the label value
        """
        result = self.label
        if self.details and self.details.formatted_address:
            result = self.details.formatted_address
        return result


    def __str__(self):
        return self.display_name
