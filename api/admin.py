from django.contrib import admin
from . import models

admin.site.register(models.Comment)
admin.site.register(models.CustomUser)
admin.site.register(models.Problem)
admin.site.register(models.Topic)
admin.site.register(models.TestCase)