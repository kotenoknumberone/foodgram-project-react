from django.contrib.auth.models import AbstractUser
from django.db import models


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

class Follow(models.Model):
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return f'{self.user} / {self.author}'

