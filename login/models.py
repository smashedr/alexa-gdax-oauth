from __future__ import unicode_literals

from django.db import models


class TokenDatabase(models.Model):
    key = models.CharField('API Key', max_length=255, primary_key=True)
    code = models.CharField('API Code', max_length=255)
    password = models.CharField('API Password', max_length=255)
    secret = models.CharField('API Secret', max_length=255)
