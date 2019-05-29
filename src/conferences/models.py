from django.db import models
from django.contrib.auth import get_user_model

# This is so that we create a new actor each time a user is saved.
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Actor(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

@receiver(post_save, sender=User)
def _post_save_user_handler(sender, **kwargs):
    Actor(user = kwargs['instance']).save() if kwargs['created'] else None

class Conference(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    website = models.CharField(max_length = 255, unique = True)
    info = models.CharField(max_length = 4096)

    startDate = models.DateField()
    abstractDate = models.DateField()
    submissionDate = models.DateField()
    presentationDate = models.DateField()
    endDate = models.DateField()

    chairedBy = models.ForeignKey(Actor, on_delete = models.CASCADE)

class Submission(models.Model):
    abstract = models.CharField(max_length = 255)
    fullPaper = models.CharField(max_length = 25500, null = True)
    metaInfo = models.CharField(max_length = 10000, null = True)
    submitter = models.ForeignKey(Actor, on_delete = models.CASCADE)

class PcMemberIn(models.Model):
    description = models.CharField(max_length=1024)
    actor = models.ForeignKey(Actor, on_delete = models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete = models.CASCADE)

################################################################################

def loggedActor(view):
    return Actor.objects.get(pk=view.request.user.id)

