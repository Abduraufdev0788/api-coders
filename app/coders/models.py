from django.db import models

class Coder(models.Model):
    nickname = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=120, unique=True)
    country = models.CharField(max_length=50)
    bio = models.TextField(null=True, blank=True)
    rating = models.IntegerField(default=1500)
    points_total = models.IntegerField(default=0)
    total_submissions = models.IntegerField(default=0)
    accepted_submissions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}. {self.nickname} -- -- -- {self.country}"
