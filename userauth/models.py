from django.db import models
from django.contrib.auth.models import User
from post.models import Post
from django.db.models.signals import post_save


# create a user file to save all the media
def user_directory_path(instance, filename):
    return f"user_{instance.user.id}/{filename}"


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)
    bio = models.TextField(max_length=200, null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    picture = models.ImageField(
        upload_to=user_directory_path,
        null=True,
        blank=True,
        default="img/default.jpg",
        verbose_name="profile-Picture",
    )
    favourite = models.ManyToManyField(Post)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        if self.user.first_name:
            return self.user.first_name
        return f"user{self.user.id}"


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)
