from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    email = models.EmailField(max_length=254,
                              unique=True)
    username = models.CharField(max_length=150,
                                unique=True, )
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'last_name',
        'password',]
        
    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Subscribe(models.Model):

    subscriber = models.ForeignKey(
                                User, 
                                related_name='follower',
                                on_delete=models.CASCADE)
    author = models.ForeignKey(
                            User, 
                            related_name='following',
                            on_delete=models.CASCADE)
    
    class Meta:
       unique_together = ("subscriber", "author")