from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image

# Create your models here.
class Province(models.Model):
    """Model representing the provinces"""
    name = models.CharField(max_length=40, help_text='Enter a province name')

    def __str__(self):
        """String representing the Model object."""
        return self.name

class Type(models.Model):
    """Model representing the type of route"""
    name = models.CharField(max_length = 100, help_text="Enter the type of route")

    def __str__(self):
        """String representing the Type object"""
        return self.name

class Route(models.Model):
    """Model representing the Route"""
    name = models.CharField(max_length=100, help_text='Enter the route name')
    author = models.ForeignKey(User, on_delete=models.RESTRICT)
    length = models.IntegerField(help_text='Enter the length of the route')
    province = models.ForeignKey(Province, on_delete=models.RESTRICT, null=True)
    type = models.ForeignKey(Type, on_delete=models.RESTRICT, null=True)
    gpx = models.FileField(null=True, blank=True, upload_to='gpx')

    class Meta:
        ordering = ['name']

    def __str__(self):
        """String representing the Route oject"""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record"""
        return reverse('route-detail', args=[str(self.id)])
    
class RouteComment(models.Model):
    """Model represeting the description of a specific route"""
    route = models.ForeignKey('Route', on_delete=models.RESTRICT, null=True)
    date = models.DateField(help_text="Date of the hike")
    author = models.ForeignKey(User, on_delete=models.RESTRICT)
    comment = models.TextField(max_length=1000, help_text="Description of the route")
    score = models.DecimalField(max_digits=3, decimal_places=1, help_text="Score for the route")

    def __str__(self):
        return str(self.route)
    
    class Meta:
        ordering = ['route', 'date']

class RoutePhoto(models.Model):
    """Model representing the photo's for a Route"""
    route = models.ForeignKey('Route', on_delete=models.RESTRICT, null=True)
    author = models.ForeignKey(User, on_delete=models.RESTRICT)
    comment = models.CharField(max_length=200, help_text="Give a comment")
    image = models.ImageField(upload_to='images/%Y/%m/%d/')

    def save(self):
        # Resizing the image, for less storage usage

        super().save() # Save image first

        img = Image.open(self.image.path) # Open using self

        if img.height > 700:
            new_img = (700, 700)
            img.thumbnail(new_img)
            img.save(self.image.path) # Saving image at the same path

    def __str__(self):
        return self.comment

    class meta:
        ordering = ['comment']
    