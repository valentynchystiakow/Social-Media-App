# imports libraries
from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4
from datetime import datetime

# defines User
User = get_user_model()

# Create your models here.
# Creates user profile model
class Profile(models.Model):

    # model fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    location = models.CharField(max_length=100, blank=True)

    # returns string representation of the profile for admin interface
    def __str__(self):
        return self.user.username
    

#  creates post model
class Post(models.Model):
    # model fields, UUIDField can also be used for unique identifiers
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    # returns string representation of the post for admin interface
    def __str__(self):
        return self.user
    

# creates like model to track likes on posts
class LikePost(models.Model):
    # model fields
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    # returns string representation of the like for admin interface
    def __str__(self):
        return self.username
    


# creates follower count model to track user profile followers 
class FollowersCount(models.Model):
    # model fields
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user
    



