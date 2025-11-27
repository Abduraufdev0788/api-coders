from django.db import models
from app.contests.models import Contest

class Problem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    max_score = models.IntegerField(default=100)
    time_limit_ms = models.IntegerField(default=1000)
    memory_limit_kb = models.IntegerField(default=65536)
    created_at = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        unique_together = ('contest', 'code')


