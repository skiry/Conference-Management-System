import re

from django.db import models
from django.contrib.auth import get_user_model

# This is so that we create a new actor each time a user is saved.
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Actor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def isConferenceChair(self, conferenceId):
        if self.conference_set.filter(id=conferenceId).first() is None:
            return "notConferenceChair"
        return "Ok"


@receiver(post_save, sender=User)
def _post_save_user_handler(sender, **kwargs):
    Actor(user=kwargs['instance']).save() if kwargs['created'] else None


class Section(models.Model):
    name = models.CharField(max_length=128)
    session_chair = models.ForeignKey(Actor, on_delete=models.CASCADE, null=True)

    @staticmethod
    def alreadyExists(sectionName):
        if Section.objects.filter(name=sectionName).exists():
            return "alreadyExists"
        return "Ok"

    @staticmethod
    def exists(sectionName):
        if Section.objects.filter(name=sectionName).exists():
            return "Ok"
        return "doesNotExist"

    def getSection(sections, name):
        for section in sections:
            if section.name == name:
                return section


class Conference(models.Model):
    name = models.CharField(max_length=255, unique=True)
    website = models.CharField(max_length=255, unique=True)
    info = models.CharField(max_length=4096)

    start_date = models.DateField()
    abstract_date = models.DateField()
    submission_date = models.DateField()
    bidding_date = models.DateField()
    presentation_date = models.DateField()
    end_date = models.DateField()

    chairedBy = models.ForeignKey(Actor, on_delete=models.CASCADE)
    evaluated = models.BooleanField(default=False)

    sections = models.ManyToManyField(Section, null=True)

    def hasSection(self, section):
        if self.sections.filter(name=section):
            return "alreadyExists"
        return "Ok"

    def isNewDateAfterCurrent(self, data):
        if self is None:
            return "doesNotExist"

        if self.abstract_date >= data['abstract_date']:
            return "dateBefore"

        if self.submission_date >= data['submission_date']:
            return "dateBefore"

        if self.presentation_date >= data['presentation_date']:
            return "dateBefore"

        if self.end_date >= data['end_date']:
            return "dateBefore"

        return "Ok"

    def checkProposalSubmit(self):
        if self is None:
            return "doesNotExist"

        if self.end_date < self.start_date:
            return "checkDates"

        if self.submission_date < self.abstract_date:
            return "checkDates"

        if self.bidding_date < self.submission_date \
                or self.bidding_date > self.presentation_date:
            return "checkDates"

        if self.presentation_date > self.end_date:
            return "checkDates"

        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, self.website) is None:
            return "websiteNotOk"

        return "Ok"

    def updateDates(self, data):
        self.abstract_date = data['abstract_date']
        self.submission_date = data['submission_date']
        self.presentation_date = data['presentation_date']
        self.end_date = data['end_date']

        self.save()

    def actorIsPCMember(self, actor):
        if self is None:
            return "doesNotExist"
        if self.pcmemberin_set.filter(actor_id=actor.id).first() is None:
            return "notPCMember"
        return "Ok"

    def getPCMemberIn(self, actor):
        return self.pcmemberin_set.filter(actor_id=actor.id).first()

    def isChairedBy(self, actor):
        if self is None:
            return "doesNotExist"
        if self.chairedBy.id != actor.id:
            return "notConferenceChair"
        return "Ok"

    def isEvaluated(self):
        if self.evaluated:
            return "alreadyEvaluated"
        return "Ok"


# this is to automatically add the chair as a pc member
# makes things easier down the road.
@receiver(post_save, sender=Conference)
def _post_save_conference_handler(sender, **kwargs):
    if kwargs['created']:
        conf = kwargs['instance']
        PcMemberIn(description="Created the conference.", conference=conf, actor=conf.chairedBy).save()


class Submission(models.Model):
    title = models.CharField(max_length=128)
    abstract = models.FileField(upload_to='abstracts')
    full_paper = models.FileField(upload_to='full-papers', null=True)
    meta_info = models.CharField(max_length=10000, null=True)
    submitter = models.ForeignKey(Actor, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    chosen_section = models.ForeignKey(Section, on_delete=models.DO_NOTHING, null=True)
    result = models.BooleanField(default=False)

    def actorIsSubmissionAuthor(self, actor):
        if self is None:
            return "doesNotExist"
        if self.submitter.id == actor.id:
            return "actorIsSubmissionAuthor"
        return "Ok"

    def actorIsNotChair(self, actor):
        if self is None:
            return "doesNotExist"
        if self.conference.chairedBy.id != actor.id:
            return "actorIsNotConferenceChair"
        return "Ok"

    def isChairOfConference(self, member):
        if self is None:
            return "doesNotExist"
        if self.conference.chairedBy.id == member.actor.id:
            return "chairOfConference"
        return "Ok"

    def updateInfo(self, data):
        self.title = data['title']
        self.abstract = data['abstract']
        self.full_paper = data['full_paper']
        self.meta_info = data['meta_info']
        self.save()

    def hasSection(self):
        if self.chosen_section is not None:
            return "hasSection"
        return "Ok"

    @staticmethod
    def allSubmissionsGraded(submissions, result):
        for submission in submissions:
            for review in submission.reviewassignment_set.all():
                if review.grade == result:
                    return "notAllGraded"
        return "Ok"


class Participants(models.Model):
    paper = models.ForeignKey(Submission, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    @staticmethod
    def alreadyRegistered(participants, actor):
        for x in participants:
            if x.actor == actor:
                return "alreadyRegistered"
        return "Ok"


class BiddingValues:
    DEFAULT = 1
    E = 'Want to Evaluate'
    N = 'Neutral'
    R = 'Refuse to Evaluate'
    CHOICES = (
        (0, 'Want to Evaluate'),
        (1, 'Neutral'),
        (2, 'Refuse to Evaluate'),
    )


class GradingValues:
    DEFAULT = 0
    N = 'Not Graded'
    SA = 'Strong Accept'
    A = 'Accept'
    WA = 'Weak Accept'
    B = 'Borderline'
    WR = 'Weak Reject'
    R = 'Reject'
    SR = 'Strong Reject'
    CHOICES = (
        (0, 'Not Graded'),
        (1, 'Strong Accept'),
        (2, 'Accept'),
        (3, 'Weak Accept'),
        (4, 'Borderline'),
        (5, 'Weak Reject'),
        (6, 'Reject'),
        (7, 'Strong Reject'),
    )


class PcMemberIn(models.Model):
    description = models.CharField(max_length=1024)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE)

    def biddingValueFor(self, submission_id):
        bid = self.bidding_set.filter(id=submission_id).first()

        if bid is None:
            return BiddingValues.N

        return bid.getBid()

    def isMemberOfConference(self, conference):
        if self is None:
            return "doesNotExist"
        if self.conference != conference:
            return "notMemberOfConference"
        return "Ok"

    def alreadyAssigned(self, pcMemberId, submissionId):
        if self is None:
            return "doesNotExist"
        if self.reviewassignment_set.filter(pcmember_id=pcMemberId).filter(
                submission_id=submissionId).first() is not None:
            return "alreadyAssigned"
        return "Ok"

    def isChair(self):
        if self is None:
            return "doesNotExist"
        if self.conference.chairedBy.id == self.actor.id:
            return "chairOfConference"
        return "Ok"

    @staticmethod
    def userExists(pcmembers, name):
        ok = 0
        for x in pcmembers:
            if x.actor.user.name == name:
                ok = 1
        if ok == 1:
            return "Ok"
        return "userDoesNotExist"

    @staticmethod
    def getUser(users, name):
        for user in users:
            if user.actor.user.name == name:
                return user


class Bidding(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    pcmember = models.ForeignKey(PcMemberIn, on_delete=models.CASCADE)
    bid = models.PositiveSmallIntegerField(default=1, choices=BiddingValues.CHOICES)

    def getBid(self):
        for x in BiddingValues.CHOICES:
            if self.bid == x[0]:
                return x[1]

    @staticmethod
    def getBidByMember(submission, member, biddings):
        res = list(filter(lambda bid: bid.submission == submission and bid.pcmember == member, biddings))
        if res:
            return res[0].getBid()
        return BiddingValues.N


class SubmissionRemark(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    pcmember = models.ForeignKey(PcMemberIn, on_delete=models.CASCADE)
    content = models.CharField(max_length=1024)


class ReviewAssignment(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    pcmember = models.ForeignKey(PcMemberIn, on_delete=models.CASCADE)
    grade = models.PositiveSmallIntegerField(default=1, choices=GradingValues.CHOICES)

    def getGrade(self):
        for x in GradingValues.CHOICES:
            if self.grade == x[0]:
                return x[1]


class EvaluationResult(models.Model):
    grade = models.PositiveSmallIntegerField(default=1, choices=GradingValues.CHOICES)
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE)

    def getGrade(self):
        for x in GradingValues.CHOICES:
            if self.grade == x[0]:
                return x[1]


################################################################################

def loggedActor(view):
    return Actor.objects.get(pk=view.request.user.id)
