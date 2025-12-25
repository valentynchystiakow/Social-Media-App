# imports libraries
from django.contrib import admin

# imports models
from .models import Profile, Post , LikePost, FollowersCount

# registers Profile model to admin interface
admin.site.register(Profile)
# registers Post model to admin interface
admin.site.register(Post)
# registers LikePost model to admin interface
admin.site.register(LikePost)
# registers FollowersCount model to admin interface
admin.site.register(FollowersCount)