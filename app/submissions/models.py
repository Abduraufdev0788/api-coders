from django.db import models
from app.contests.models import Contest
from app.coders.models import Coder
from app.problems.models import Problem


class Submission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('wrong_answer', 'Wrong Answer'),
        ('runtime_error', 'Runtime Error'),
        ('time_limit', 'Time Limit Exceeded'),
        ('compilation_error', 'Compilation Error'),
        ('partial', 'Partial Score'),
    ]
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    coder = models.ForeignKey(Coder, on_delete=models.PROTECT)
    language = models.CharField(max_length=50)
    code = models.TextField()
    status = models.CharField(choices=STATUS_CHOICES, default="pending")
    score = models.IntegerField(default=0)
    attempt_no = models.IntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)
    judged_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        ordering = ["-submitted_at"]
    

    def __str__(self):
        return f"{self.id}.{self.coder.nickname}  -- -- -- {self.language}"
