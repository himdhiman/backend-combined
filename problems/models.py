from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
from problems.helper import convert_string_to_list
from authentication.helper import set_fixed_data


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class CompanyTag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Problem(models.Model):
    choose = (
        ("E", "Easy"),
        ("M", "Medium"),
        ("H", "Hard"),
    )
    created_by = models.EmailField(max_length=150)
    title = models.CharField(max_length=100)
    problem_statement = models.TextField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    input_format = models.TextField(blank=True, null=True)
    constraints = models.TextField(blank=True, null=True)
    output_format = models.TextField(blank=True, null=True)
    max_score = models.IntegerField(blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    problem_level = models.CharField(max_length=20, choices=choose)
    accuracy = models.IntegerField(default=0)
    totalSubmissions = models.IntegerField(default=0)
    sample_Tc = models.IntegerField(default=0)
    total_Tc = models.IntegerField(default=0)
    created_At = models.DateField(auto_now=True)
    memory_Limit = models.IntegerField(null=True, blank=True, default=1)
    time_Limit = models.IntegerField(null=True, blank=True, default=1)
    publically_visible = models.BooleanField(default=True)
    approved_by_admin = models.BooleanField(default=False)
    up_votes = models.IntegerField(default=0)
    down_votes = models.IntegerField(default=0)
    company_tags = models.ManyToManyField(
        CompanyTag, verbose_name="list of company tags"
    )
    media_ids = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"({self.id}) - " + self.title


class ProblemMedia(models.Model):
    image = models.ImageField(upload_to="ProblemMedia")


class Bookmark(models.Model):
    user = models.EmailField(max_length=150)
    data = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user


class Submission(models.Model):
    created_By = models.CharField(max_length=50, blank=False)
    problem_Id = models.IntegerField(blank=False)
    language = models.CharField(max_length=50, blank=False)
    task_id = models.TextField(null=True, blank=True)
    code = models.TextField(blank=False)
    status = models.CharField(max_length=30, default="Queued")
    error = models.TextField(null=True, blank=True)
    test_Cases_Passed = models.IntegerField(null=True, blank=True)
    total_Test_Cases = models.IntegerField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    submission_Date_Time = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return str(self.id)


class UpvotesDownvote(models.Model):
    mail_Id = models.CharField(max_length=50, blank=False)
    upvote = models.TextField(null=True, blank=True)
    downvote = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.mail_Id)


class Editorial(models.Model):
    problem_Id = models.IntegerField(null=True, blank=True)
    cpp17 = models.TextField(null=True, blank=True)
    java = models.TextField(null=True, blank=True)
    python2 = models.TextField(null=True, blank=True)
    python3 = models.TextField(null=True, blank=True)
    cpp14 = models.TextField(null=True, blank=True)
    c = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.problem_Id)


class SavedCode(models.Model):
    created_By = models.CharField(max_length=50, blank=False)
    problem_Id = models.IntegerField(null=True, blank=True)
    code = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=50, blank=False)
    submission_Date_Time = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.created_By


@receiver(pre_save, sender=Problem)
def before_saving_problem(sender, instance, *args, **kwargs):
    if not instance.id:
        return
    curr_instance = Problem.objects.get(id=instance.id)
    send_data = {}

    if curr_instance.problem_level == "E":
        send_data["field"] = "easy"
    elif curr_instance.problem_level == "M":
        send_data["field"] = "medium"
    elif curr_instance.problem_level == "H":
        send_data["field"] = "hard"

    if curr_instance.approved_by_admin == False and instance.approved_by_admin:
        send_data["type"] = "increase"
        set_fixed_data.set_data(request_data=send_data)

    elif curr_instance.approved_by_admin and instance.approved_by_admin == False:
        send_data["type"] = "decrease"
        set_fixed_data.set_data(request_data=send_data)
    return


@receiver(pre_delete, sender=Problem)
def before_deleting_problem(sender, instance, *args, **kwargs):
    blobs = settings.BUCKET.list_blobs(prefix=f"media/TestCases/{instance.id}/")
    for blob in blobs:
        blob.delete()
    pids = convert_string_to_list.convert_to_list(data=instance.media_ids)
    for i in pids:
        pm = ProblemMedia.objects.filter(id=int(i))
        pm.delete()
    return


@receiver(pre_delete, sender=ProblemMedia)
def before_deleting_ProblemMedia(sender, instance, *args, **kwargs):
    instance.image.storage.delete(instance.image.name)
    return
