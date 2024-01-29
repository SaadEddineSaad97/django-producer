from django.db import models


class Message(models.Model):
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.text} - {self.timestamp}"

