from django.db import models

from django.contrib.auth.models import User

class Submission(models.Model):

    DBOPTS = (
        ('genage_model', 'GenAge model organisms'),
        ('gendr', 'GenDR gene manipulations'),
        ('longevity', 'LongevityMap'),
    )

    date_submitted = models.DateField(auto_now_add=True)
    submitter_name = models.CharField(max_length=300, blank=True, null=True)
    submitter_email = models.EmailField(blank=True, null=True)
    database = models.TextField(max_length=20, choices=DBOPTS)
    submission = models.TextField()
    is_added = models.BooleanField(default=False)
    added_by = models.ForeignKey(User, blank=True, null=True)
    added_on = models.DateField(blank=True, null=True)

    class Meta:
        app_label = "beta_daa"

    def __unicode__(self):
        return u'{} - {} ({})'.format(self.date_submitted, self.submitter_name, self.submitter_email)

