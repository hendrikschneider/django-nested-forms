'''Test-only models.

https://docs.djangoproject.com/en/2.0/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications
'''

from django.db import models

# Models
class SampleParentModel(models.Model):
    sample_field = models.CharField(max_length=8)

    class Meta:
        db_table = 'parent'

class SampleChildModel(models.Model):
    sample_field = models.CharField(max_length=8)

class SampleRelatedModel(models.Model):
    parent = models.ForeignKey(SampleParentModel)
    sample_field = models.CharField(max_length=8)
