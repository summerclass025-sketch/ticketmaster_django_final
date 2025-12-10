from django.db import models


class SearchHistory(models.Model):
    genre = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    total_results = models.IntegerField()
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.genre} in {self.city} ({self.total_results} results)"
class FavoriteEvent(models.Model):
    name = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, blank=True)
    date = models.CharField(max_length=100, blank=True)
    ticket_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name