from django.db import models


class User(models.Model):
    login = models.CharField(primary_key=True, max_length=30)
    password = models.CharField(max_length=30)
    name = models.CharField(null=True, blank=True, max_length=20)
    lang = models.CharField(null=True, blank=True, max_length=2)
    theme = models.CharField(null=True, blank=True, max_length=10)
