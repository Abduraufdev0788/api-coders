from django.db import models
from app.coders.models import Coder
from app.contests.models import Contest

class RatingChange(models.Model):
    coder = models.ForeignKey(Coder, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    old_rating = models.IntegerField()
    new_rating = models.IntegerField()
    delta = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        indexes = [
            models.Index(fields=['coder', 'created_at'])
        ]