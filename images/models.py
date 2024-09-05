from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UploadedImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    result = models.CharField(max_length=255, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.image.url}"