from django.db import models

class Contest(models.Model):
    CHOISE  =[
        ("public", "Public"),
        ("private", "Private")
    ]
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    visibility = models.CharField(choices=CHOISE, default='public')
    finalized = models.BooleanField(default=False)
    problems_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Contest  ---  {self.title}"


        


