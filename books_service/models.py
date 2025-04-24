from django.db import models


class Book(models.Model):
    class StatusChoices(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=255, choices=StatusChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_free = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} ({self.author})"
