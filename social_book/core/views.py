# imports libraries
from django.shortcuts import render 
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from itertools import chain
import random
# imports models
from .models import Profile,Post,LikePost,FollowersCount

# Create your views here.
# marks home view function as requiring user to be logged in decorator
@login_required(login_url='signin')
# defines index view function 
def index(request):

    # defines user and user profile objects from database
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # defines user_following_list and feed variables
    user_following_list = []
    feed = []

    # filters user_following objects based on the logged-in user
    user_following = FollowersCount.objects.filter(follower=request.user.username)

    # appends username in user_following objects to user_following_list
    for users in user_following:
        user_following_list.append(users.user)

    # loops through user_following_list to extract posts from database
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        # appends posts to feed
        feed.append(feed_lists)

    # uses chain function to flatten feed list and converts it to an iterable list
    feed_list = list(chain(*feed))

    # suggestions feature
    all_users = User.objects.all()
    user_following_all = []


    # loops through user_following objects to get usernames of users being followed
    for user in user_following:
        user_list = User.objects.get(username=user.user)
        # appends usernames to user_following_all
        user_following_all.append(user_list)
    
    # creates a list of users that the logged-in user is not following
    new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    # removes the logged-in user from the suggestions list
    final_suggestions_list = [x for x in list(new_suggestions_list) if ( x not in list(current_user))]
    # uses random to shuffle the suggestions list
    random.shuffle(final_suggestions_list)

    # defines username_profile and username_profile_list variables
    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    # uses chain function to flatten username_profile_list list and converts it to an iterable list
    suggestions_username_profile_list = list(chain(*username_profile_list))


    # renders index page with user profile, feed and suggestions context
    return render(request, 'index.html', {'user_profile': user_profile, 'posts':feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})



# marks follow view function as requiring user to be logged in decorator
@login_required(login_url='signin')
# defines follow view function
def follow(request):
    # checks if request method is POST
    if request.method == 'POST':
        # defines follower and user variables to store form data
        follower = request.POST['follower']
        user = request.POST['user']

        # checks if a FollowersCount object exists for the follower and user
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            # if it exists, delete the FollowersCount object (unfollow)
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            # redirects to the profile page of the user being unfollowed
            return redirect('/profile/'+user)
        else:
            # if it does not exist, create a new FollowersCount object (follow)
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            # redirects to the profile page of the user being followed
            return redirect('/profile/'+user)
    else:
        return redirect('/')


# marks settings view function as requiring user to be logged in decorator
@login_required(login_url='signin')
# defines account settings view function
def settings(request):

    # defines user_profile variable to hold Profile object of the logged-in user
    user_profile = Profile.objects.get(user=request.user)

    # checks if the request method is POST
    if request.method == 'POST':
        
        # checks if image field is empty
        if request.FILES.get('image') == None:
            # sets image variable to current profile image
            image = user_profile.profileimg
            # sets bio and location variables to form data
            bio = request.POST['bio']
            location = request.POST['location']

            # updates user profile fields
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        # if image field is not empty
        if request.FILES.get('image') != None:
            # sets image, bio, and location variables to form data
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']
            # updates user profile fields
            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            # saves updated profile to the database
            user_profile.save()
        # redirects to main page after saving profile updates
        return redirect('/')
    return render(request, 'settings.html', {'user_profile': user_profile})

# defines signup view function
def signup(request):

    # checks if the request method is POST
    if request.method == 'POST':
        # defines variables to hold form data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        # checks if password and confirm password match
        if password == password2:
            # checks if email already exists in the database
            if User.objects.filter(email=email).exists():
                # if email already exists, display error message and redirect to signup page
                messages.info(request, 'Email is already taken')
                return redirect('signup')
            # checks if username already exists in the database
            elif User.objects.filter(username=username).exists():
                # if username already exists, display error message and redirect to signup page
                messages.info(request, 'Username is already taken')
                return redirect('signup')
            else:
                # if email and username do not exist, create new user and redirect to login page
                user = User.objects.create_user(username=username, email=email, password=password)
                # saves user to the database
                user.save()

                # logs user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # creates a Profile object for the new user based on the User model
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user = user_model.id)
                # saves profile to the database
                new_profile.save()
                # redirects to settings page after successful signup
                return redirect('settings')

        else:
            # if passwords do not match, display error message and redirect to signup page
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    else:
        return render(request, 'signup.html')
    

# defines login view function
def signin(request):
   
    #  checks if method is POST
    if request.method == 'POST':
        # defines variables to hold form data
        username = request.POST['username']
        password = request.POST['password']

        # defines user variable to authenticate user
        user = auth.authenticate(username=username, password=password)

        # checks if user is not None
        if user is not None:
            # if user is authenticated(credentials are valid), log them in and redirect to index(home) page
            auth.login(request,user)
            return redirect('/')
        else:
            # if user credentials are invalid, display error message and redirect to login page
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')
    

# decorator that requires user to be logged in to access logout view
@login_required(login_url='signin')
# defines logout view function
def logout(request):
    # logs out the user
    auth.logout(request)
    # redirects to signin page after logout
    return redirect('/signin')


# decorator that requires user to be logged in to access upload view
@login_required(login_url='signin')
# defines upload view functiondef upload(request):
def upload(request): 

    
    # checks if request method is POST
    if request.method == 'POST':
       # defines user, image and caption variables to store post form data
        user = request.user.username 
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        # creates a new Post object based on the Post model and saves it to the database
        new_post = Post.objects.create(user=user,image = image,caption=caption)
        new_post.save()

        # redirects to index(home) page after successful upload
        return redirect('/')


    else:
        return redirect( '/')


# decorator that requires user to be logged in to access profile view
@login_required(login_url='signin')
# defines search view function
def search(request):
    # defines user and user profile objects
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # checks if request method is POST
    if request.method == 'POST':
        # defines username variable to store search form data
        username = request.POST['username']
        # defines username_object variable to store search results
        username_object = User.objects.filter(username__icontains=username)

        # defines username_profile and username_profile_list variables for storing search results
        username_profile = []
        username_profile_list = []

        # loops through username_object queryset to extract usernames
        for users in username_object:
            # appends username to username_profile list
            username_profile.append(users.id)

        # loops through username_profile list to extract user ids
        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)


        # uses chain function to flatten username_profile_list list and converts it to a list
        username_profile_list = list(chain(*username_profile_list))

    # renders templaate with search results context
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


# decorator that requires user to be logged in to access like_post view
@login_required(login_url='signin')
# defines like_post view function
def like_post(request):

    username = request.user.username
    # gets post_id from the request's GET parameters to retrieve post by id from database
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    # filters LikePost objects to check if the user has already liked the post
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        # creates a new LikePost object if the user has not liked the post yet
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        # increments the number of likes on the post
        post.no_of_likes = post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        # removes the LikePost object if the user has already liked the post
        like_filter.delete()
        # decrements the number of likes on the post
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')
    

# decorator that requires user to be logged in to access profile view
@login_required(login_url='signin')
# defines profile view function
def profile(request, pk):

    # defines user object based on the username(pk) passed in the URL
    user_object = User.objects.get(username=pk)
    # gets Profile object for the user
    user_profile = Profile.objects.get(user=user_object)
    # filters user posts based on the username(pk)
    user_posts = Post.objects.filter(user=pk)
    # determines the number of posts made by the user
    user_post_length = len(user_posts)

    # checks if the logged-in user is following the profile user
    follower = request.user.username
    # defines user variable to store profile username
    user = pk

    # checks if a FollowersCount object exists for the logged-in user and the profile user
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    # defines user_followers and user_following variables to store follower and following counts
    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    # creates context dictionary to pass data to the profile template
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }
    return render(request, 'profile.html', context) 